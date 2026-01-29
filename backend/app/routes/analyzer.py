"""
Analyzer API Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
import re

from app.schemas.requests import AnalyzeRepoRequest
from app.schemas.responses import (
    AnalyzeRepoResponse,
    AnalysisResult,
    ProjectExplanation,
    ResumeBulletPoint,
    VivaQuestion,
    InterviewQA,
    ErrorResponse
)
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService
from app.utils.prompts import get_system_prompt, get_analysis_prompt

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Router & Services
# --------------------------------------------------

router = APIRouter()
github_service = GitHubService()

# --------------------------------------------------
# Helper: Extract JSON from LLM response
# --------------------------------------------------

def extract_json_from_llm(text: str) -> dict:
    """
    Extract valid JSON from LLM markdown response
    """
    if not text:
        raise ValueError("Empty LLM response")

    # Remove markdown code fences
    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {cleaned}")
        raise ValueError(f"Invalid JSON returned by LLM: {str(e)}")

# --------------------------------------------------
# Routes
# --------------------------------------------------

@router.post(
    "/analyze-repo",
    response_model=AnalyzeRepoResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_repository(request: AnalyzeRepoRequest):
    """
    Analyze a GitHub repository and generate interview/resume materials
    """

    try:
        logger.info(f"Starting analysis for repository: {request.repo_url}")

        # Initialize LLM
        llm_service = LLMService()

        # -------------------------
        # Step 1: GitHub Analysis
        # -------------------------
        logger.info("Fetching repository data from GitHub...")
        repo_data = await github_service.analyze_repository(request.repo_url)

        logger.info(
            f"Repository fetched: {repo_data['owner']}/{repo_data['repo_name']} "
            f"(files: {repo_data['total_files']})"
        )

        # -------------------------
        # Step 2: Prompt creation
        # -------------------------
        logger.info("Generating prompts...")
        system_prompt = get_system_prompt()
        user_prompt = get_analysis_prompt(repo_data, request.focus)

        # -------------------------
        # Step 3: LLM call
        # -------------------------
        logger.info("Calling Groq LLM...")
        llm_response = await llm_service.generate_analysis(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        logger.info(f"Raw LLM response: {llm_response}")

        # -------------------------
        # Step 4: Parse LLM JSON
        # -------------------------
        raw_text = llm_response.get("answer")

        if not raw_text:
            raise ValueError("LLM response missing 'answer' field")

        parsed_response = extract_json_from_llm(raw_text)

        logger.info("Parsed LLM JSON successfully")

        # -------------------------
        # Step 5: Validate structure
        # -------------------------
        llm_service.validate_response_structure(parsed_response)

        # -------------------------
        # Step 6: Convert to models
        # -------------------------

        explanation = ProjectExplanation(**parsed_response["explanation"])

        resume_bullets = [
            ResumeBulletPoint(**bullet)
            for bullet in parsed_response["resume_bullets"]
        ]

        viva_questions = [
            VivaQuestion(**question)
            for question in parsed_response["viva_questions"]
        ]

        interview_qa = [
            InterviewQA(**qa)
            for qa in parsed_response["interview_qa"]
        ]

        analysis_result = AnalysisResult(
            repo_name=repo_data["repo_name"],
            repo_owner=repo_data["owner"],
            explanation=explanation,
            resume_bullets=resume_bullets,
            viva_questions=viva_questions,
            interview_qa=interview_qa
        )

        logger.info("Analysis completed successfully")

        return AnalyzeRepoResponse(
            success=True,
            data=analysis_result,
            message="Repository analyzed successfully"
        )

    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "analyzer",
        "github_service": "operational",
        "llm_service": "operational"
    }


# --------------------------------------------------
# Chat Endpoint
# --------------------------------------------------

@router.post("/chat")
async def chat_about_repo(request: dict):
    """
    Chat about analyzed repository
    """

    try:
        question = request.get("question", "")
        context = request.get("context", {})

        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        llm_service = LLMService()

        repo_context = f"""
Repository: {context.get('repo_owner')}/{context.get('repo_name')}

Overview: {context.get('explanation', {}).get('overview', '')}
Key Features: {', '.join(context.get('explanation', {}).get('key_features', []))}
Tech Stack: {', '.join(context.get('explanation', {}).get('tech_stack', []))}
Architecture: {context.get('explanation', {}).get('architecture', '')}
Challenges: {', '.join(context.get('explanation', {}).get('challenges_solved', []))}
Impact: {context.get('explanation', {}).get('impact', '')}
"""

        system_prompt = (
            "You are a helpful assistant that answers questions about GitHub repositories. "
            "Base answers only on the provided context. "
            "If information is missing, say you do not have that data."
        )

        user_prompt = f"""
Context:
{repo_context}

Question:
{question}
"""

        response = await llm_service.generate_analysis(system_prompt, user_prompt)

        answer = response.get(
            "answer",
            response.get("text", "Sorry, I could not generate an answer.")
        )

        return {"answer": answer}

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
