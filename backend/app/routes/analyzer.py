"""
Analyzer API Routes
"""

from backend.app.services import llm_service
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Services will be initialized on demand
github_service = GitHubService()


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
    
    Args:
        request: Repository analysis request
        
    Returns:
        Analysis results with project explanation, resume bullets, viva questions, and interview Q&A
    """
    
    try:
        logger.info(f"Starting analysis for repository: {request.repo_url}")
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Step 1: Extract repository data from GitHub
        logger.info("Fetching repository data from GitHub...")
        repo_data = await github_service.analyze_repository(request.repo_url)
        
        logger.info(f"Repository data fetched: {repo_data['owner']}/{repo_data['repo_name']}")
        logger.info(f"Total files: {repo_data['total_files']}")
        
        # Step 2: Generate prompts
        logger.info("Generating LLM prompts...")
        system_prompt = get_system_prompt()
        user_prompt = get_analysis_prompt(repo_data, request.focus)
        
        # Step 3: Call LLM for analysis
        logger.info("Calling Groq LLM for analysis...")
        llm_response = await llm_service.generate_analysis(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Step 4: Validate response structure
        logger.info("Validating LLM response...")
        logger.info(f"LLM Response: {llm_response}")  # ADD THIS LINE
        llm_service.validate_response_structure(llm_response)
        
        # Step 5: Parse response into Pydantic models
        logger.info("Parsing response into structured format...")
        
        # Parse explanation
        explanation = ProjectExplanation(**llm_response["explanation"])
        
        # Parse resume bullets
        resume_bullets = [
            ResumeBulletPoint(**bullet)
            for bullet in llm_response["resume_bullets"]
        ]
        
        # Parse viva questions
        viva_questions = [
            VivaQuestion(**question)
            for question in llm_response["viva_questions"]
        ]
        
        # Parse interview Q&A
        interview_qa = [
            InterviewQA(**qa)
            for qa in llm_response["interview_qa"]
        ]
        
        # Step 6: Build final result
        analysis_result = AnalysisResult(
            repo_name=repo_data["repo_name"],
            repo_owner=repo_data["owner"],
            explanation=explanation,
            resume_bullets=resume_bullets,
            viva_questions=viva_questions,
            interview_qa=interview_qa
        )
        
        logger.info("Analysis completed successfully")
        
        # Return success response
        return AnalyzeRepoResponse(
            success=True,
            data=analysis_result,
            message="Repository analyzed successfully"
        )
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP error during analysis: {e.detail}")
        raise e
        
    except Exception as e:
        # Catch all other errors
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "analyzer",
        "github_service": "operational",
        "llm_service": "operational"
    }


@router.post("/chat")
async def chat_about_repo(request: dict):
    """
    Chat about analyzed repository
    
    Args:
        request: Contains question and context (analysis results)
        
    Returns:
        AI answer about the repository
    """
    try:
        question = request.get('question', '')
        context = request.get('context', {})
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Build context from analysis results
        repo_context = f"""
Repository: {context.get('repo_owner')}/{context.get('repo_name')}

Project Overview: {context.get('explanation', {}).get('overview', '')}

Key Features: {', '.join(context.get('explanation', {}).get('key_features', []))}

Tech Stack: {', '.join(context.get('explanation', {}).get('tech_stack', []))}

Architecture: {context.get('explanation', {}).get('architecture', '')}

Challenges: {', '.join(context.get('explanation', {}).get('challenges_solved', []))}

Impact: {context.get('explanation', {}).get('impact', '')}
"""
        
        system_prompt = """You are a helpful assistant that answers questions about GitHub repositories.
Base your answers ONLY on the provided repository context. Be concise and accurate.
If the information is not in the context, say "I don't have that information in the analysis."
Keep answers under 150 words."""
        
        user_prompt = f"""Context about the repository:
{repo_context}

User question: {question}

Provide a helpful, concise answer based on the context above."""
        
        response = await llm_service.generate_analysis(system_prompt, user_prompt)
        
        # Extract answer from response
        answer = response.get('answer', response.get('text', 'Sorry, I could not generate an answer.'))
        
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))