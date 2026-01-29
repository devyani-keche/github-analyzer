"""
Response schemas for API outputs
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ResumeBulletPoint(BaseModel):
    """Individual resume bullet point"""
    point: str = Field(..., description="Formatted resume bullet point")


class VivaQuestion(BaseModel):
    """Viva examination question with answer"""
    question: str = Field(..., description="Viva question")
    answer: str = Field(..., description="Expected answer")
    difficulty: str = Field(..., description="easy, medium, or hard")


class InterviewQA(BaseModel):
    """Interview question and answer pair"""
    question: str = Field(..., description="Interview question")
    answer: str = Field(..., description="Sample answer")
    category: str = Field(..., description="technical, behavioral, or project-specific")


class ProjectExplanation(BaseModel):
    """Structured project explanation"""
    overview: str = Field(..., description="High-level project overview")
    key_features: List[str] = Field(..., description="Main features/capabilities")
    tech_stack: List[str] = Field(..., description="Technologies used")
    architecture: str = Field(..., description="System architecture description")
    challenges_solved: List[str] = Field(..., description="Key problems solved")
    impact: str = Field(..., description="Project impact/value")


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    repo_name: str = Field(..., description="Repository name")
    repo_owner: str = Field(..., description="Repository owner")
    explanation: ProjectExplanation = Field(..., description="Project explanation")
    resume_bullets: List[ResumeBulletPoint] = Field(..., description="Resume bullet points")
    viva_questions: List[VivaQuestion] = Field(..., description="Viva questions")
    interview_qa: List[InterviewQA] = Field(..., description="Interview Q&A")


class AnalyzeRepoResponse(BaseModel):
    """API response wrapper"""
    success: bool = Field(..., description="Whether analysis was successful")
    data: Optional[AnalysisResult] = Field(None, description="Analysis results")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(default=False)
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Detailed error information")