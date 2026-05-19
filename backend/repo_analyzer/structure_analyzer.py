# structure_analyzer.py
"""
Repository structure analysis.
"""

from typing import Optional, Dict, Any, List
from collections import defaultdict
from .fetcher import RepoFetcher


class StructureAnalyzer:
    """Analyze overall repository structure."""

    def __init__(self, fetcher: RepoFetcher):
        """
        Initialize analyzer with fetcher.

        Args:
            fetcher: RepoFetcher instance
        """
        self.fetcher = fetcher

    def analyze_structure(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze repository structure.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Dict with structure analysis
        """
        try:
            tree = self.fetcher.get_repo_tree(owner, repo, branch)

            if not tree:
                return None

            # Analyze structure
            total_files = 0
            total_dirs = 0
            root_items = {'files': [], 'directories': []}
            depth_distribution = defaultdict(int)
            extension_counts = defaultdict(int)

            for item in tree:
                path = item['path']
                depth = path.count('/')

                # Count depth
                depth_distribution[depth] += 1

                if item['type'] == 'blob':
                    total_files += 1

                    # Track file extensions
                    if '.' in path:
                        ext = path.split('.')[-1].lower()
                        extension_counts[ext] += 1

                    # Root level files
                    if depth == 0:
                        root_items['files'].append(path)

                elif item['type'] == 'tree':
                    total_dirs += 1

                    # Root level directories
                    if depth == 0:
                        root_items['directories'].append(path)

            # Get top-level directory structure
            top_level_dirs = root_items['directories']

            # Get top 10 file extensions
            top_extensions = sorted(
                extension_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            return {
                'total_files': total_files,
                'total_directories': total_dirs,
                'max_depth': max(depth_distribution.keys()) if depth_distribution else 0,
                'root_files': root_items['files'],
                'root_directories': root_items['directories'],
                'top_extensions': dict(top_extensions),
                'url': f'https://github.com/{owner}/{repo}/tree/{branch}'
            }

        except Exception as e:
            print(f"Error analyzing structure: {e}")
            return None


def analyze_structure(
    repo_owner: str,
    repo_name: str,
    branch: str,
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze repository structure.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with structure analysis or None if failed
    """
    fetcher = RepoFetcher(github_pat)
    analyzer = StructureAnalyzer(fetcher)
    return analyzer.analyze_structure(repo_owner, repo_name, branch)
