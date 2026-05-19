# checks/docs.py
"""
Documentation directory checker.
"""

from typing import List, Dict, Any
from .base import BaseChecker


class DocsChecker(BaseChecker):
    """Checker for documentation directories."""

    def get_checks(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'has_markdown',
                'function': lambda: self._has_file_matching(['.md']),
                'severity': 'error',
                'pass_message': 'Markdown documentation found',
                'fail_message': 'No .md files found'
            },
            {
                'name': 'has_architecture_docs',
                'function': lambda: self._has_dir_matching(['architecture']) or self._has_file_matching(['architecture', 'diagram']),
                'severity': 'info',
                'pass_message': 'Architecture documentation found',
                'fail_message': 'No architecture docs or diagrams found'
            },
            {
                'name': 'has_examples',
                'function': lambda: self._has_dir_matching(['examples', 'templates']),
                'severity': 'info',
                'pass_message': 'Examples/templates found',
                'fail_message': 'No examples/templates folder found'
            },
            {
                'name': 'has_scripts',
                'function': lambda: self._has_dir_matching(['scripts']),
                'severity': 'info',
                'pass_message': 'Scripts directory found',
                'fail_message': 'No scripts folder found'
            },
            {
                'name': 'has_tests',
                'function': lambda: self._has_dir_matching(['tests', 'integration', 'e2e']),
                'severity': 'warning',
                'pass_message': 'Test directories found',
                'fail_message': 'No tests/integration/e2e folders found'
            },
            {
                'name': 'has_contribution_docs',
                'function': lambda: self._has_file_matching(['CONTRIBUTING', 'CODE_OF_CONDUCT']),
                'severity': 'info',
                'pass_message': 'Contribution documentation found',
                'fail_message': 'No CONTRIBUTING or CODE_OF_CONDUCT found'
            },
            {
                'name': 'has_changelog',
                'function': lambda: self._has_file_matching(['CHANGELOG', 'HISTORY']),
                'severity': 'info',
                'pass_message': 'Changelog/version documentation found',
                'fail_message': 'No CHANGELOG or HISTORY found'
            },
            {
                'name': 'has_license',
                'function': lambda: self._has_file_matching(['LICENSE', 'COPYING']),
                'severity': 'warning',
                'pass_message': 'License file found',
                'fail_message': 'No LICENSE file found'
            }
        ]
