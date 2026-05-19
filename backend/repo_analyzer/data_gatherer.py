# data_gatherer.py
"""
Data gathering functions for repository analysis.
Collects data from various analyzers and returns in JSON format.
"""

from typing import Dict, Any, Optional, List
import json
from .readme_analyzer import analyze_readme as _analyze_readme
from .dependency_analyzer import analyze_dependencies as _analyze_dependencies
from .structure_analyzer import analyze_structure as _analyze_structure
from .naming_analyzer import analyze_naming_conventions as _analyze_naming
from .git_metadata_analyzer import analyze_git_metadata as _analyze_git


VALID_ANALYSIS_TYPES = [
    "readme",
    "dependencies",
    "structure",
    "naming",
    "git_metadata"
]


def gather_comprehensive_data(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gather all available analysis data for a repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict containing all analysis results in JSON format
    """
    data = {
        'repository': {
            'owner': repo_owner,
            'name': repo_name,
            'branch': branch
        },
        'analyses': {}
    }

    # Run all analyzers
    readme_data = _analyze_readme(repo_owner, repo_name, branch, github_pat)
    if readme_data:
        data['analyses']['readme'] = readme_data

    dependency_data = _analyze_dependencies(
        repo_owner, repo_name, branch, github_pat)
    if dependency_data:
        data['analyses']['dependencies'] = dependency_data

    structure_data = _analyze_structure(
        repo_owner, repo_name, branch, github_pat)
    if structure_data:
        data['analyses']['structure'] = structure_data

    naming_data = _analyze_naming(repo_owner, repo_name, branch, github_pat)
    if naming_data:
        data['analyses']['naming'] = naming_data

    git_data = _analyze_git(repo_owner, repo_name, branch, github_pat)
    if git_data:
        data['analyses']['git_metadata'] = git_data

    return data


def gather_specific_data(
    repo_owner: str,
    repo_name: str,
    branch: str,
    analysis_types: List[str],
    github_pat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gather specific types of analysis data for a repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        analysis_types: List of analysis types to run (e.g., ['readme', 'dependencies'])
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict containing requested analysis results in JSON format

    Raises:
        ValueError: If invalid analysis type is provided
    """
    # Validate analysis types
    for analysis_type in analysis_types:
        if analysis_type not in VALID_ANALYSIS_TYPES:
            raise ValueError(
                f"Invalid analysis type: {analysis_type}. "
                f"Must be one of: {VALID_ANALYSIS_TYPES}"
            )

    data = {
        'repository': {
            'owner': repo_owner,
            'name': repo_name,
            'branch': branch
        },
        'analyses': {}
    }

    # Run only requested analyzers
    if 'readme' in analysis_types:
        readme_data = _analyze_readme(
            repo_owner, repo_name, branch, github_pat)
        if readme_data:
            data['analyses']['readme'] = readme_data

    if 'dependencies' in analysis_types:
        dependency_data = _analyze_dependencies(
            repo_owner, repo_name, branch, github_pat)
        if dependency_data:
            data['analyses']['dependencies'] = dependency_data

    if 'structure' in analysis_types:
        structure_data = _analyze_structure(
            repo_owner, repo_name, branch, github_pat)
        if structure_data:
            data['analyses']['structure'] = structure_data

    if 'naming' in analysis_types:
        naming_data = _analyze_naming(
            repo_owner, repo_name, branch, github_pat)
        if naming_data:
            data['analyses']['naming'] = naming_data

    if 'git_metadata' in analysis_types:
        git_data = _analyze_git(repo_owner, repo_name, branch, github_pat)
        if git_data:
            data['analyses']['git_metadata'] = git_data

    return data
