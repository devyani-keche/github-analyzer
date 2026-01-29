"""
Utility helper functions
"""

import re
from typing import Dict, Any


def clean_text(text: str, max_length: int = 10000) -> str:
    """
    Clean and truncate text content
    
    Args:
        text: Raw text to clean
        max_length: Maximum length to keep
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might break JSON
    text = text.replace('\x00', '')
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text.strip()


def format_repo_context(repo_data: Dict[str, Any]) -> str:
    """
    Format repository data into readable context
    
    Args:
        repo_data: Repository information dictionary
        
    Returns:
        Formatted string
    """
    
    context = f"""
Repository: {repo_data['owner']}/{repo_data['repo_name']}
Total Files: {repo_data['total_files']}

Folder Structure:
{', '.join(repo_data['folder_structure'][:30])}

README:
{repo_data['readme'][:2000]}
"""
    
    if repo_data.get('important_files'):
        context += "\n\nKey Files:\n"
        for file_path in list(repo_data['important_files'].keys())[:5]:
            context += f"- {file_path}\n"
    
    return context


def sanitize_json_string(text: str) -> str:
    """
    Sanitize string for JSON encoding
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Replace problematic characters
    replacements = {
        '\n': ' ',
        '\r': ' ',
        '\t': ' ',
        '"': "'",
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in ['\n', '\t'])
    
    return text


def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$'
    return bool(re.match(pattern, url.rstrip('/')))


def truncate_content(content: str, max_chars: int = 5000) -> str:
    """
    Intelligently truncate content
    
    Args:
        content: Content to truncate
        max_chars: Maximum characters
        
    Returns:
        Truncated content
    """
    if len(content) <= max_chars:
        return content
    
    # Try to truncate at a newline
    truncated = content[:max_chars]
    last_newline = truncated.rfind('\n')
    
    if last_newline > max_chars * 0.8:  # If newline is in last 20%
        return truncated[:last_newline] + "\n..."
    
    return truncated + "..."