# github_fetcher.py
"""
GitHub API utilities for fetching repository contents.
"""

import requests
from typing import List, Tuple, Optional


class GitHubFetcher:
    """Fetch repository contents from GitHub API."""

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

    def fetch_directory_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str = 'main'
    ) -> Tuple[List[str], List[str], str]:
        """
        Fetch contents of a directory from GitHub recursively.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to directory in repository
            branch: Branch name (default: 'main')

        Returns:
            Tuple of (files, directories, api_url)
            Files and directories will have full paths relative to the specified directory

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
        all_items = tree_data.get('tree', [])

        # Filter items that are in the specified path
        files = []
        directories = []

        # Normalize path
        normalized_path = path.strip('/')

        for item in all_items:
            item_path = item['path']

            # Check if item is in the specified directory
            if normalized_path:
                if not item_path.startswith(normalized_path + '/'):
                    continue
                # Get relative path from the specified directory
                relative_path = item_path[len(normalized_path) + 1:]
            else:
                # Root directory
                relative_path = item_path

            if item['type'] == 'blob':
                files.append(relative_path)
            elif item['type'] == 'tree':
                directories.append(relative_path)

        api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'

        return files, directories, api_url
