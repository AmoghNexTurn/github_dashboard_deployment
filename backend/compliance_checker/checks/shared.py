# checks/shared.py
"""
Shared code directory checker.
"""

from typing import List, Dict, Any
from .base import BaseChecker


class SharedChecker(BaseChecker):
    """Checker for shared/common code directories."""

    def get_checks(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'has_utils',
                'function': lambda: self._has_dir_matching(['utils', 'helpers']),
                'severity': 'warning',
                'pass_message': 'Utilities/helpers directory found',
                'fail_message': 'No utils/helpers folder found'
            },
            {
                'name': 'has_types',
                'function': lambda: self._has_dir_matching(['types', 'interfaces']),
                'severity': 'info',
                'pass_message': 'Types/interfaces directory found',
                'fail_message': 'No types/interfaces folder found'
            },
            {
                'name': 'has_schemas',
                'function': lambda: self._has_dir_matching(['schemas', 'validators']),
                'severity': 'info',
                'pass_message': 'Schemas/validators directory found',
                'fail_message': 'No schemas/validators folder found'
            },
            {
                'name': 'has_api_clients',
                'function': lambda: self._has_dir_matching(['api', 'clients']),
                'severity': 'info',
                'pass_message': 'API clients directory found',
                'fail_message': 'No api/clients folder found'
            },
            {
                'name': 'has_constants',
                'function': lambda: self._has_dir_matching(['constants', 'config']),
                'severity': 'info',
                'pass_message': 'Constants/config directory found',
                'fail_message': 'No constants/config folder found'
            },
            {
                'name': 'has_libs',
                'function': lambda: self._has_dir_matching(['packages', 'libs']),
                'severity': 'info',
                'pass_message': 'Internal libraries directory found',
                'fail_message': 'No packages/libs folder found'
            },
            {
                'name': 'has_test_utils',
                'function': lambda: self._has_dir_matching(['test-utils', 'testing']),
                'severity': 'info',
                'pass_message': 'Test utilities directory found',
                'fail_message': 'No test-utils folder found'
            },
            {
                'name': 'has_readme',
                'function': lambda: self._has_file_matching(['README.md', 'readme.md']),
                'severity': 'warning',
                'pass_message': 'README documentation found',
                'fail_message': 'No README.md found'
            }
        ]
