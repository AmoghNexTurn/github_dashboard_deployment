# fetcher.py
"""
GitHub API utilities for recursive repository traversal.
"""

import requests
from typing import List, Dict, Any, Optional


class RepoFetcher:
    """Fetch repository contents recursively from GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize fetcher with optional GitHub token.

        Args:
            token: GitHub personal access token (optional, required for private repos)
        """
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'

    def get_repo_tree(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> List[Dict[str, Any]]:
        """
        Get complete repository file tree recursively.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name (default: 'main')

        Returns:
            List of file/directory objects with path, type, size, sha

        Raises:
            Exception: If API request fails
        """
        # First get the commit SHA for the branch
        ref_url = f'https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}'
        ref_response = requests.get(ref_url, headers=self.headers)

        if ref_response.status_code != 200:
            raise Exception(
                f'Failed to get branch ref: {ref_response.status_code} - {ref_response.text}'
            )

        commit_sha = ref_response.json()['object']['sha']

        # Get the commit to find tree SHA
        commit_url = f'https://api.github.com/repos/{owner}/{repo}/git/commits/{commit_sha}'
        commit_response = requests.get(commit_url, headers=self.headers)

        if commit_response.status_code != 200:
            raise Exception(
                f'Failed to get commit: {commit_response.status_code} - {commit_response.text}'
            )

        tree_sha = commit_response.json()['tree']['sha']

        # Get recursive tree
        tree_url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1'
        tree_response = requests.get(tree_url, headers=self.headers)

        if tree_response.status_code != 200:
            raise Exception(
                f'Failed to get tree: {tree_response.status_code} - {tree_response.text}'
            )

        tree_data = tree_response.json()
        return tree_data.get('tree', [])

    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str = 'main'
    ) -> Optional[str]:
        """
        Get content of a specific file.

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            branch: Branch name (default: 'main')

        Returns:
            File content as string, or None if file not found or is binary

        Raises:
            Exception: If API request fails
        """
        url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
        params = {'ref': branch}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            return None

        data = response.json()

        # Check if it's a file (not directory)
        if data.get('type') != 'file':
            return None

        # Get content (it's base64 encoded)
        import base64
        try:
            content = base64.b64decode(data['content']).decode('utf-8')
            return content
        except Exception:
            # Binary file or encoding error
            return None

    def find_files(
        self,
        tree: List[Dict[str, Any]],
        patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find files matching specific patterns in tree.

        Args:
            tree: Repository tree from get_repo_tree()
            patterns: List of filename patterns to match (case-insensitive)

        Returns:
            List of matching file objects
        """
        matches = []

        for item in tree:
            if item['type'] != 'blob':  # Only files, not trees
                continue

            filename = item['path'].split('/')[-1].lower()

            for pattern in patterns:
                if pattern.lower() in filename:
                    matches.append(item)
                    break

        return matches
