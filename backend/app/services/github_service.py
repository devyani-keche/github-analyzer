"""
GitHub Service - Handles GitHub API interactions
"""

import os
import re
import base64
from typing import Dict, List, Optional, Tuple
import httpx
from fastapi import HTTPException


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def parse_github_url(self, repo_url: str) -> Tuple[str, str]:
        """
        Extract owner and repo name from GitHub URL
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
        """
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, repo_url)
        
        if not match:
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL format"
            )
        
        owner, repo = match.groups()
        repo = repo.replace('.git', '')
        
        return owner, repo
    
    async def fetch_readme(self, owner: str, repo: str) -> str:
        """
        Fetch repository README content
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 404:
                    return "No README found"
                
                response.raise_for_status()
                data = response.json()
                
                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise HTTPException(
                        status_code=403,
                        detail="GitHub API rate limit exceeded or repository is private"
                    )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Failed to fetch README: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching README: {str(e)}"
                )
    
    async def fetch_repo_tree(self, owner: str, repo: str) -> List[Dict]:
        """
        Fetch repository file tree structure
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of file/directory information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/main?recursive=1"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                # Try 'master' if 'main' doesn't exist
                if response.status_code == 404:
                    url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/master?recursive=1"
                    response = await client.get(url, headers=self.headers, timeout=10.0)
                
                response.raise_for_status()
                data = response.json()
                
                return data.get('tree', [])
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise HTTPException(
                        status_code=403,
                        detail="GitHub API rate limit exceeded"
                    )
                # Return empty tree if we can't fetch it
                return []
            except Exception as e:
                return []
    
    async def fetch_file_content(self, owner: str, repo: str, file_path: str) -> Optional[str]:
        """
        Fetch content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to file in repository
            
        Returns:
            File content as string or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Check file size (skip files > 1MB)
                if data.get('size', 0) > 1_000_000:
                    return None
                
                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
                
            except Exception:
                return None
    
    def filter_important_files(self, tree: List[Dict], max_files: int = 10) -> List[str]:
        """
        Filter and prioritize important source files
        
        Args:
            tree: Repository tree structure
            max_files: Maximum number of files to return
            
        Returns:
            List of important file paths
        """
        important_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go',
            '.rs', '.rb', '.php', '.swift', '.kt', '.cs', '.scala', '.sql'
        }
        
        important_filenames = {
            'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
            'pom.xml', 'build.gradle', 'Dockerfile', 'docker-compose.yml',
            'setup.py', 'pyproject.toml', 'Makefile'
        }
        
        config_files = []
        source_files = []
        
        for item in tree:
            if item['type'] != 'blob':
                continue
            
            path = item['path']
            filename = os.path.basename(path)
            _, ext = os.path.splitext(filename)
            
            # Skip test files and large directories
            if any(skip in path.lower() for skip in ['test', 'node_modules', '.git', 'dist', 'build']):
                continue
            
            # Prioritize config files
            if filename in important_filenames:
                config_files.append(path)
            # Then source files
            elif ext in important_extensions:
                source_files.append(path)
        
        # Combine and limit
        selected_files = config_files[:3] + source_files[:max_files-len(config_files[:3])]
        return selected_files[:max_files]
    
    async def analyze_repository(self, repo_url: str) -> Dict:
        """
        Complete repository analysis
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing repository data
        """
        owner, repo = self.parse_github_url(repo_url)
        
        # Fetch README
        readme = await self.fetch_readme(owner, repo)
        
        # Fetch repository tree
        tree = await self.fetch_repo_tree(owner, repo)
        
        # Get folder structure summary
        folders = set()
        for item in tree:
            if '/' in item['path']:
                folder = item['path'].split('/')[0]
                folders.add(folder)
        
        # Get important files
        important_files_paths = self.filter_important_files(tree)
        
        # Fetch content of important files
        file_contents = {}
        for file_path in important_files_paths:
            content = await self.fetch_file_content(owner, repo, file_path)
            if content:
                # Limit content size
                file_contents[file_path] = content[:5000]  # First 5000 chars
        
        return {
            "owner": owner,
            "repo_name": repo,
            "readme": readme,
            "folder_structure": sorted(list(folders)),
            "important_files": file_contents,
            "total_files": len([item for item in tree if item['type'] == 'blob'])
        }