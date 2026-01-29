"""
Prompt templates for LLM-based analysis
"""

def get_system_prompt() -> str:
    """Get system prompt for LLM"""
    return """You are an expert technical interviewer, resume consultant, and project evaluator.

Your task is to analyze GitHub repository information and generate high-quality, professional content for:
1. Project explanations suitable for interviews
2. Resume bullet points following best practices
3. Viva/oral examination questions with answers
4. Technical interview questions and answers

Guidelines:
- Base your analysis ONLY on the provided repository data
- Do not hallucinate or make up information
- Use professional, interview-appropriate language
- Be specific and technical where appropriate
- Format output as valid JSON matching the required schema
- Resume bullets should follow the STAR method (Situation, Task, Action, Result)
- Questions should range from easy to hard difficulty
- Interview questions should cover technical, architectural, and problem-solving aspects

Output ONLY valid JSON without any markdown formatting or additional text."""


def get_analysis_prompt(repo_data: dict, focus: str = "all") -> str:
    """
    Generate user prompt for repository analysis
    
    Args:
        repo_data: Dictionary containing repository information
        focus: Analysis focus (all, resume, interview, viva)
        
    Returns:
        Formatted prompt string
    """
    
    # Build file contents section
    files_section = ""
    if repo_data.get("important_files"):
        files_section = "\n\n## KEY SOURCE FILES:\n"
        for file_path, content in repo_data["important_files"].items():
            files_section += f"\n### {file_path}\n```\n{content[:2000]}\n```\n"
    
    prompt = f"""Analyze this GitHub repository and generate comprehensive interview/resume preparation materials.

## REPOSITORY INFORMATION:

**Repository:** {repo_data['owner']}/{repo_data['repo_name']}
**Total Files:** {repo_data['total_files']}

## FOLDER STRUCTURE:
{', '.join(repo_data['folder_structure'][:20])}

## README:
{repo_data['readme'][:3000]}

{files_section}

## REQUIRED OUTPUT:

Generate a JSON object with the following structure:

{{
  "explanation": {{
    "overview": "2-3 sentence high-level summary of the project",
    "key_features": ["feature1", "feature2", "feature3", ...],
    "tech_stack": ["technology1", "technology2", ...],
    "architecture": "Description of system architecture and design patterns used",
    "challenges_solved": ["challenge1", "challenge2", ...],
    "impact": "What problem does this solve and what value does it provide"
  }},
  "resume_bullets": [
    {{"point": "Action-oriented bullet point following STAR method"}},
    {{"point": "Another quantifiable achievement"}},
    {{"point": "Technical contribution highlighting skills"}},
    {{"point": "Impact-focused accomplishment"}},
    {{"point": "Complex problem solved"}}
  ],
  "viva_questions": [
    {{"question": "Easy conceptual question", "answer": "Clear answer", "difficulty": "easy"}},
    {{"question": "Medium question about implementation", "answer": "Detailed answer", "difficulty": "medium"}},
    {{"question": "Hard question about architecture/design", "answer": "Comprehensive answer", "difficulty": "hard"}},
    {{"question": "Another medium question", "answer": "Answer", "difficulty": "medium"}},
    {{"question": "Another hard question", "answer": "Answer", "difficulty": "hard"}}
  ],
  "interview_qa": [
    {{"question": "Technical question about implementation", "answer": "Sample answer", "category": "technical"}},
    {{"question": "Question about project challenges", "answer": "Sample answer", "category": "project-specific"}},
    {{"question": "Behavioral question about teamwork/decisions", "answer": "Sample answer", "category": "behavioral"}},
    {{"question": "Architecture/design question", "answer": "Sample answer", "category": "technical"}},
    {{"question": "Problem-solving scenario", "answer": "Sample answer", "category": "technical"}}
  ]
}}

IMPORTANT:
- Generate at least 5 resume bullets, 5 viva questions, and 5 interview Q&As
- Make questions progressively harder
- Base everything on actual repository content
- Use specific technical terms from the codebase
- Resume bullets should start with strong action verbs
- Include quantifiable metrics where possible
- Output ONLY the JSON object, no other text
"""
    
    return prompt


def get_focused_prompt(repo_data: dict, focus: str) -> str:
    """
    Generate focused prompt for specific analysis type
    
    Args:
        repo_data: Repository data
        focus: Specific focus area
        
    Returns:
        Tailored prompt
    """
    
    if focus == "resume":
        return get_resume_focused_prompt(repo_data)
    elif focus == "interview":
        return get_interview_focused_prompt(repo_data)
    elif focus == "viva":
        return get_viva_focused_prompt(repo_data)
    else:
        return get_analysis_prompt(repo_data, focus)


def get_resume_focused_prompt(repo_data: dict) -> str:
    """Generate resume-focused prompt"""
    
    return f"""Analyze this repository and generate 8-10 professional resume bullet points.

Repository: {repo_data['owner']}/{repo_data['repo_name']}

README:
{repo_data['readme'][:2000]}

Guidelines:
- Follow STAR method (Situation, Task, Action, Result)
- Start with strong action verbs (Developed, Implemented, Architected, Optimized, etc.)
- Include quantifiable metrics where possible
- Highlight technical skills and technologies
- Show impact and results
- Keep each bullet to 1-2 lines
- Be specific about what YOU did

Output JSON only:
{{
  "resume_bullets": [
    {{"point": "bullet point 1"}},
    {{"point": "bullet point 2"}},
    ...
  ]
}}
"""


def get_interview_focused_prompt(repo_data: dict) -> str:
    """Generate interview-focused prompt"""
    
    return f"""Generate 10 technical interview questions and answers for this project.

Repository: {repo_data['owner']}/{repo_data['repo_name']}

README:
{repo_data['readme'][:2000]}

Categories:
- Technical implementation questions
- Architecture and design questions
- Problem-solving scenarios
- Project-specific challenges
- Behavioral questions about development process

Output JSON only:
{{
  "interview_qa": [
    {{"question": "...", "answer": "...", "category": "technical/behavioral/project-specific"}},
    ...
  ]
}}
"""


def get_viva_focused_prompt(repo_data: dict) -> str:
    """Generate viva-focused prompt"""
    
    return f"""Generate 10 viva/oral examination questions with answers for this project.

Repository: {repo_data['owner']}/{repo_data['repo_name']}

README:
{repo_data['readme'][:2000]}

Include:
- 3 easy questions (basic concepts)
- 4 medium questions (implementation details)
- 3 hard questions (architecture, trade-offs, alternatives)

Output JSON only:
{{
  "viva_questions": [
    {{"question": "...", "answer": "...", "difficulty": "easy/medium/hard"}},
    ...
  ]
}}
"""