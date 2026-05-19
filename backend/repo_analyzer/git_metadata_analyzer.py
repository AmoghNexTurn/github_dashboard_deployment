# git_metadata_analyzer.py
"""
Git metadata analysis (commits, branches, etc.).
"""

from typing import Optional, Dict, Any, List
import requests
from .fetcher import RepoFetcher


class GitMetadataAnalyzer:
    """Analyze git metadata from repositories."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize analyzer with optional GitHub token.

        Args:
            token: GitHub personal access token (optional)
        """
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'

    def analyze_metadata(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze git metadata.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Dict with git metadata analysis
        """
        try:
            # Get recent commits
            commits = self._get_recent_commits(owner, repo, branch)

            # Get branches
            branches = self._get_branches(owner, repo)

            # Get repository info
            repo_info = self._get_repo_info(owner, repo)

            if not commits:
                return None

            # Analyze commit messages
            commit_analysis = self._analyze_commits(commits)

            return {
                'recent_commits': {
                    'count': len(commits),
                    'messages': [c['message'] for c in commits[:10]],
                    'analysis': commit_analysis
                },
                'branches': {
                    'count': len(branches),
                    'names': [b['name'] for b in branches[:20]]
                },
                'repository': repo_info,
                'url': f'https://github.com/{owner}/{repo}'
            }

        except Exception as e:
            print(f"Error analyzing git metadata: {e}")
            return None

    def _get_recent_commits(
        self,
        owner: str,
        repo: str,
        branch: str,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Get recent commits from a branch."""
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        params = {
            'sha': branch,
            'per_page': limit
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            return []

        commits = response.json()

        return [
            {
                'sha': c['sha'][:7],
                'message': c['commit']['message'],
                'author': c['commit']['author']['name'],
                'date': c['commit']['author']['date']
            }
            for c in commits
        ]

    def _get_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get list of branches."""
        url = f'https://api.github.com/repos/{owner}/{repo}/branches'

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return []

        return [
            {
                'name': b['name'],
                'sha': b['commit']['sha'][:7]
            }
            for b in response.json()
        ]

    def _get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information."""
        url = f'https://api.github.com/repos/{owner}/{repo}'

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return {}

        data = response.json()

        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'language': data.get('language'),
            'stars': data.get('stargazers_count'),
            'forks': data.get('forks_count'),
            'open_issues': data.get('open_issues_count'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at')
        }

    def _analyze_commits(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze commit message patterns."""
        if not commits:
            return {}

        # Check for conventional commits
        conventional_pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:'
        conventional_count = 0

        for commit in commits:
            import re
            if re.match(conventional_pattern, commit['message'].lower()):
                conventional_count += 1

        return {
            'conventional_commits_ratio': conventional_count / len(commits) if commits else 0,
            'uses_conventional_commits': conventional_count > len(commits) * 0.5
        }


def analyze_git_metadata(
    repo_owner: str,
    repo_name: str,
    branch: str,
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze git metadata (commits, branches, etc.).

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with git metadata analysis or None if failed
    """
    analyzer = GitMetadataAnalyzer(github_pat)
    return analyzer.analyze_metadata(repo_owner, repo_name, branch)
