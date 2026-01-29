"""
LLM Service - Handles Groq API interactions for content generation
"""

import os
import json
import asyncio
from typing import Dict
import httpx
from fastapi import HTTPException


class LLMService:
    """Service for interacting with Groq LLM API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Remove any whitespace
        self.api_key = self.api_key.strip()
        
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"  # Current Groq model
        self.max_tokens = 8000
        self.temperature = 0.3  # Lower temperature for more consistent structured outputs
    
    async def generate_analysis(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 2
    ) -> Dict:
        """
        Generate analysis using Groq LLM
        
        Args:
            system_prompt: System instruction prompt
            user_prompt: User query with repository data
            max_retries: Number of retries on failure
            
        Returns:
            Parsed JSON response from LLM
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries + 1):
                try:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract content from response
                    content = data['choices'][0]['message']['content']
                    
                    # Parse JSON response
                    try:
                        result = json.loads(content)
                        return result
                    except json.JSONDecodeError as e:
                        # For chat responses, might be plain text
                        if "answer" in content or "text" in content:
                            return {"answer": content}
                        
                        # Try to extract JSON from markdown code blocks if present
                        if "```json" in content:
                            json_str = content.split("```json")[1].split("```")[0].strip()
                            result = json.loads(json_str)
                            return result
                        elif "```" in content:
                            json_str = content.split("```")[1].split("```")[0].strip()
                            result = json.loads(json_str)
                            return result
                        else:
                            # Return as plain text answer for chat
                            return {"answer": content}
                    
                except httpx.HTTPStatusError as e:
                    error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                    print(f"Groq API Error Response: {error_detail}")  # Debug logging
                    
                    if e.response.status_code == 429:
                        # Rate limit - retry with backoff
                        if attempt < max_retries:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise HTTPException(
                            status_code=429,
                            detail="Groq API rate limit exceeded. Please try again later."
                        )
                    elif e.response.status_code == 401:
                        raise HTTPException(
                            status_code=500,
                            detail="Invalid Groq API key"
                        )
                    else:
                        raise HTTPException(
                            status_code=e.response.status_code,
                            detail=f"Groq API error: {str(e)}"
                        )
                        
                except httpx.TimeoutException:
                    if attempt < max_retries:
                        continue
                    raise HTTPException(
                        status_code=504,
                        detail="LLM request timed out. Repository may be too large."
                    )
                    
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error generating analysis: {str(e)}"
                    )
        
        # Should not reach here
        raise HTTPException(
            status_code=500,
            detail="Failed to generate analysis after retries"
        )
    
    def validate_response_structure(self, response: Dict) -> bool:
        """
        Validate that response has required structure
        
        Args:
            response: LLM response dictionary
            
        Returns:
            True if valid, raises exception otherwise
        """
        
        required_keys = {
            "explanation": ["overview", "key_features", "tech_stack", 
                          "architecture", "challenges_solved", "impact"],
            "resume_bullets": [],
            "viva_questions": [],
            "interview_qa": []
        }
        
        # Check top-level keys
        for key in required_keys:
            if key not in response:
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM response missing required field: {key}"
                )
        
        # Validate explanation structure
        explanation = response["explanation"]
        for field in required_keys["explanation"]:
            if field not in explanation:
                raise HTTPException(
                    status_code=500,
                    detail=f"Explanation missing required field: {field}"
                )
        
        # Validate lists are not empty
        if not response["resume_bullets"]:
            raise HTTPException(
                status_code=500,
                detail="No resume bullets generated"
            )
        
        if not response["viva_questions"]:
            raise HTTPException(
                status_code=500,
                detail="No viva questions generated"
            )
        
        if not response["interview_qa"]:
            raise HTTPException(
                status_code=500,
                detail="No interview Q&A generated"
            )
        
        return True