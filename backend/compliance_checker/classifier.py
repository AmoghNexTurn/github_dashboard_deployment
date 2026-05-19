# classifier.py
"""
Directory classification based on naming patterns.
"""

import re
from typing import Optional


class DirectoryClassifier:
    """Classify directories based on their names."""

    PATTERNS = {
        'frontend': [
            r'^frontend$',
            r'^client$',
            r'^web$',
            r'^ui$',
            r'^app$'
        ],
        'backend': [
            r'^backend$',
            r'^server$',
            r'^api$',
            r'^services?$'
        ],
        'infrastructure': [
            r'^infra(structure)?$',
            r'^docker$',
            r'^deployment$',
            r'^k8s$',
            r'^kubernetes$',
            r'^nginx$'
        ],
        'shared': [
            r'^shared$',
            r'^common$',
            r'^lib$',
            r'^core$',
            r'^packages$'
        ],
        'docs': [
            r'^docs?$',
            r'^scripts$',
            r'^tests?$',
            r'^examples?$'
        ]
    }

    @classmethod
    def classify(cls, path: str) -> Optional[str]:
        """
        Classify a directory based on its name.

        Args:
            path: Directory path (will extract last segment)

        Returns:
            Category name ('frontend', 'backend', etc.) or None if no match
        """
        # Extract directory name from path
        dir_name = path.rstrip('/').split('/')[-1].lower()

        # Try to match against patterns
        for category, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, dir_name):
                    return category

        return None


def classify_directory(
    repo_owner: str,
    repo_name: str,
    branch: str,
    path: str,
    github_pat: Optional[str] = None
) -> Optional[str]:
    """
    Classify a directory in a GitHub repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        path: Path to directory
        github_pat: GitHub personal access token (optional)

    Returns:
        Category name or None if classification fails
    """
    return DirectoryClassifier.classify(path)
