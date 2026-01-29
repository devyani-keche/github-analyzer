"""
Request schemas for API validation
"""

from pydantic import BaseModel, Field, HttpUrl, validator
import re


class AnalyzeRepoRequest(BaseModel):
    """Request schema for repository analysis"""
    
    repo_url: str = Field(
        ..., 
        description="GitHub repository URL",
        example="https://github.com/openai/whisper"
    )
    focus: str = Field(
        default="all",
        description="Analysis focus: 'resume', 'interview', 'viva', or 'all'",
        example="all"
    )
    
    @validator('repo_url')
    def validate_github_url(cls, v):
        """Validate that the URL is a valid GitHub repository URL"""
        pattern = r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$'
        if not re.match(pattern, v.rstrip('/')):
            raise ValueError('Invalid GitHub repository URL format')
        return v.rstrip('/')
    
    @validator('focus')
    def validate_focus(cls, v):
        """Validate focus parameter"""
        valid_focuses = ['resume', 'interview', 'viva', 'all']
        if v.lower() not in valid_focuses:
            raise ValueError(f'Focus must be one of: {", ".join(valid_focuses)}')
        return v.lower()