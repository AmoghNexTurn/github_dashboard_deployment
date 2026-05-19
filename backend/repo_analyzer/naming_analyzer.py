# naming_analyzer.py
"""
Naming convention analysis across repository files.
"""

from typing import Optional, Dict, Any, List
import re
from collections import defaultdict
from .fetcher import RepoFetcher


class NamingAnalyzer:
    """Analyze naming conventions across repository."""

    def __init__(self, fetcher: RepoFetcher):
        """
        Initialize analyzer with fetcher.

        Args:
            fetcher: RepoFetcher instance
        """
        self.fetcher = fetcher

    def analyze_naming(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze naming conventions in repository.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Dict with naming analysis
        """
        try:
            tree = self.fetcher.get_repo_tree(owner, repo, branch)

            if not tree:
                return None

            # Collect all file and directory names
            file_names = []
            dir_names = []

            for item in tree:
                name = item['path'].split('/')[-1]

                if item['type'] == 'blob':
                    # Remove extension for analysis
                    if '.' in name:
                        name_without_ext = '.'.join(name.split('.')[:-1])
                    else:
                        name_without_ext = name
                    file_names.append(name_without_ext)

                elif item['type'] == 'tree':
                    dir_names.append(name)

            # Analyze naming patterns
            file_patterns = self._analyze_patterns(file_names)
            dir_patterns = self._analyze_patterns(dir_names)

            return {
                'file_naming': {
                    'total': len(file_names),
                    'patterns': file_patterns,
                    'samples': file_names[:20]  # First 20 as samples
                },
                'directory_naming': {
                    'total': len(dir_names),
                    'patterns': dir_patterns,
                    'samples': dir_names[:20]  # First 20 as samples
                },
                'url': f'https://github.com/{owner}/{repo}/tree/{branch}'
            }

        except Exception as e:
            print(f"Error analyzing naming: {e}")
            return None

    def _analyze_patterns(self, names: List[str]) -> Dict[str, int]:
        """
        Analyze naming patterns in a list of names.

        Returns:
            Dict with pattern counts
        """
        patterns = {
            'camelCase': 0,
            'PascalCase': 0,
            'snake_case': 0,
            'kebab-case': 0,
            'UPPER_CASE': 0,
            'mixed': 0
        }

        for name in names:
            pattern = self._detect_pattern(name)
            patterns[pattern] += 1

        return patterns

    def _detect_pattern(self, name: str) -> str:
        """Detect naming pattern of a single name."""
        if not name:
            return 'mixed'

        # Check for UPPER_CASE
        if name.isupper() and '_' in name:
            return 'UPPER_CASE'

        # Check for snake_case
        if '_' in name and name.islower():
            return 'snake_case'

        # Check for kebab-case
        if '-' in name and name.islower():
            return 'kebab-case'

        # Check for PascalCase (starts with uppercase)
        if name[0].isupper() and not '_' in name and not '-' in name:
            return 'PascalCase'

        # Check for camelCase (starts with lowercase, has uppercase letters)
        if name[0].islower() and any(c.isupper() for c in name):
            return 'camelCase'

        return 'mixed'


def analyze_naming_conventions(
    repo_owner: str,
    repo_name: str,
    branch: str,
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze naming conventions across repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with naming analysis or None if failed
    """
    fetcher = RepoFetcher(github_pat)
    analyzer = NamingAnalyzer(fetcher)
    return analyzer.analyze_naming(repo_owner, repo_name, branch)
