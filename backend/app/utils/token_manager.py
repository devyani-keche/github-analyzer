from itertools import cycle
import os

class TokenManager:
    def __init__(self):
        # Get comma-separated tokens from env
        github_tokens = os.getenv("GITHUB_TOKENS", "").split(",")
        groq_tokens = os.getenv("GROQ_TOKENS", "").split(",")
        
        self.github_tokens = cycle([t.strip() for t in github_tokens if t.strip()])
        self.groq_tokens = cycle([t.strip() for t in groq_tokens if t.strip()])
    
    def get_github_token(self):
        return next(self.github_tokens)
    
    def get_groq_token(self):
        return next(self.groq_tokens)

token_manager = TokenManager()
