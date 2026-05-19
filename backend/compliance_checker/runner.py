# runner.py
"""
Main functions for running directory compliance checks.
"""

from typing import Dict, Any, Optional
from .classifier import DirectoryClassifier
from .github_fetcher import GitHubFetcher
from .checks import (
    FrontendChecker,
    BackendChecker,
    InfrastructureChecker,
    SharedChecker,
    DocsChecker
)


CHECKER_MAP = {
    'frontend': FrontendChecker,
    'backend': BackendChecker,
    'infrastructure': InfrastructureChecker,
    'shared': SharedChecker,
    'docs': DocsChecker
}


def dynamic_checklist(
    repo_owner: str,
    repo_name: str,
    branch: str,
    path: str,
    github_pat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify directory and run appropriate checks.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        path: Path to directory
        github_pat: GitHub personal access token (optional, required for private repos)

    Returns:
        Report dict with classification and check results
    """
    # Classify the directory
    category = DirectoryClassifier.classify(path)

    if category is None:
        return {
            'report': {
                'category': 'unknown',
                'url': f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}',
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'results': [{
                    'check': 'classification',
                    'passed': False,
                    'message': 'Could not classify directory type',
                    'severity': 'error'
                }]
            }
        }

    # Fetch directory contents
    fetcher = GitHubFetcher(github_pat)
    files, directories, api_url = fetcher.fetch_directory_contents(
        repo_owner, repo_name, path, branch
    )

    # Run checks
    checker_class = CHECKER_MAP[category]
    checker = checker_class(files, directories)
    results = checker.run_checks()

    # Calculate stats
    passed = sum(1 for r in results if r['passed'])
    failed = len(results) - passed

    return {
        'report': {
            'category': category,
            'url': api_url,
            'total_checks': len(results),
            'passed': passed,
            'failed': failed,
            'results': results
        }
    }


def specific_checklist(
    repo_owner: str,
    repo_name: str,
    branch: str,
    path: str,
    category: str,
    test_selection: Dict[int, bool],
    github_pat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run specific checks for a given category.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        path: Path to directory
        category: One of 'frontend', 'backend', 'infrastructure', 'shared', 'docs'
        test_selection: Dict mapping check index (1-based) to bool (enabled/disabled)
        github_pat: GitHub personal access token (optional, required for private repos)

    Returns:
        Report dict with check results
    """
    # Validate category
    if category not in CHECKER_MAP:
        return {
            'report': {
                'category': category,
                'url': f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}',
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'results': [{
                    'check': 'validation',
                    'passed': False,
                    'message': f'Invalid category: {category}',
                    'severity': 'error'
                }]
            }
        }

    # Fetch directory contents
    fetcher = GitHubFetcher(github_pat)
    files, directories, api_url = fetcher.fetch_directory_contents(
        repo_owner, repo_name, path, branch
    )

    # Run selected checks
    checker_class = CHECKER_MAP[category]
    checker = checker_class(files, directories)
    results = checker.run_checks(test_selection)

    # Calculate stats
    passed = sum(1 for r in results if r['passed'])
    failed = len(results) - passed

    return {
        'report': {
            'category': category,
            'url': api_url,
            'total_checks': len(results),
            'passed': passed,
            'failed': failed,
            'results': results
        }
    }
