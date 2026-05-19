# llm_compliance_checker/runner.py
"""
Main runner functions for LLM compliance checking.
"""

from typing import List, Dict, Optional
import re
from .llm_checker import check_with_llm
from .checklist_definitions import CATEGORY_PATTERNS


def classify_directory(path: str) -> Optional[str]:
    """Classify directory based on path name."""
    dir_name = path.rstrip('/').split('/')[-1].lower()

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, dir_name):
                return category

    return None


def check_dynamic(
    files: List[str],
    directories: List[str],
    path: str,
    url: str,
    groq_api_key: Optional[str] = None
) -> Dict:
    """
    Classify directory and run appropriate checks with LLM.

    Args:
        files: List of file paths in directory
        directories: List of directory paths
        path: Directory path for classification
        url: API URL for the directory
        groq_api_key: Groq API key (optional)

    Returns:
        Compliance report dict
    """
    category = classify_directory(path)

    if not category:
        return {
            'report': {
                'category': 'unknown',
                'url': url,
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

    return check_with_llm(files, directories, category, url, None, groq_api_key)


def check_specific(
    files: List[str],
    directories: List[str],
    category: str,
    test_selection: Dict[int, bool],
    url: str,
    groq_api_key: Optional[str] = None
) -> Dict:
    """
    Run specific checks with LLM.

    Args:
        files: List of file paths in directory
        directories: List of directory paths
        category: Directory category
        test_selection: Dict mapping check index to enabled/disabled
        url: API URL for the directory
        groq_api_key: Groq API key (optional)

    Returns:
        Compliance report dict
    """
    valid_categories = ['frontend', 'backend',
                        'infrastructure', 'shared', 'docs']

    if category not in valid_categories:
        return {
            'report': {
                'category': category,
                'url': url,
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

    return check_with_llm(files, directories, category, url, test_selection, groq_api_key)
