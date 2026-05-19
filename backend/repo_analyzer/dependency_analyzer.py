# dependency_analyzer.py
"""
Dependency file extraction and analysis.
"""

from typing import Optional, Dict, Any, List
from .fetcher import RepoFetcher


class DependencyAnalyzer:
    """Extract and analyze dependency files from repositories."""

    DEPENDENCY_FILES = {
        'javascript': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
        'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', 'poetry.lock'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
        'ruby': ['Gemfile', 'Gemfile.lock'],
        'php': ['composer.json', 'composer.lock'],
        'go': ['go.mod', 'go.sum'],
        'rust': ['Cargo.toml', 'Cargo.lock'],
        'dotnet': ['*.csproj', 'packages.config', 'project.json']
    }

    def __init__(self, fetcher: RepoFetcher):
        """
        Initialize analyzer with fetcher.

        Args:
            fetcher: RepoFetcher instance
        """
        self.fetcher = fetcher

    def find_dependencies(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> Optional[Dict[str, Any]]:
        """
        Find and extract dependency files.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Dict with dependency info or None if not found
        """
        try:
            tree = self.fetcher.get_repo_tree(owner, repo, branch)

            # Flatten all dependency patterns
            all_patterns = []
            for patterns in self.DEPENDENCY_FILES.values():
                all_patterns.extend(patterns)

            # Find dependency files
            dep_files = self.fetcher.find_files(tree, all_patterns)

            if not dep_files:
                return None

            # Extract content from all found dependency files
            dependencies = []

            for dep_file in dep_files:
                content = self.fetcher.get_file_content(
                    owner, repo, dep_file['path'], branch
                )

                if content:
                    # Determine language/ecosystem
                    ecosystem = self._detect_ecosystem(dep_file['path'])

                    dependencies.append({
                        'path': dep_file['path'],
                        'ecosystem': ecosystem,
                        'size': dep_file.get('size', 0),
                        'content': content,
                        'url': f'https://github.com/{owner}/{repo}/blob/{branch}/{dep_file["path"]}'
                    })

            if not dependencies:
                return None

            return {
                'found': len(dependencies),
                'files': dependencies
            }

        except Exception as e:
            print(f"Error finding dependencies: {e}")
            return None

    def _detect_ecosystem(self, path: str) -> str:
        """Detect ecosystem from file path."""
        filename = path.split('/')[-1].lower()

        for ecosystem, patterns in self.DEPENDENCY_FILES.items():
            for pattern in patterns:
                if pattern.replace('*', '') in filename:
                    return ecosystem

        return 'unknown'


def analyze_dependencies(
    repo_owner: str,
    repo_name: str,
    branch: str,
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find and extract dependency files from repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with dependency info or None if not found
    """
    fetcher = RepoFetcher(github_pat)
    analyzer = DependencyAnalyzer(fetcher)
    return analyzer.find_dependencies(repo_owner, repo_name, branch)
