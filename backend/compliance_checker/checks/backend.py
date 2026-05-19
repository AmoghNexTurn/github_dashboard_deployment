# checks/backend.py
"""
Backend directory checker.
"""

from typing import List, Dict, Any
from .base import BaseChecker


class BackendChecker(BaseChecker):
    """Checker for backend directories."""

    def get_checks(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'has_dependency_file',
                'function': lambda: self._has_file_matching([
                    'package.json', 'requirements.txt', 'pyproject.toml',
                    'pom.xml', 'Gemfile', 'go.mod', 'Cargo.toml'
                ]),
                'severity': 'error',
                'pass_message': 'Dependency management file found',
                'fail_message': 'No dependency file found'
            },
            {
                'name': 'has_api_dirs',
                'function': lambda: self._has_dir_matching(['routes', 'controllers', 'api']),
                'severity': 'warning',
                'pass_message': 'API/controller directories found',
                'fail_message': 'No routes/controllers/api folders found'
            },
            {
                'name': 'has_models',
                'function': lambda: self._has_dir_matching(['models', 'schemas', 'entities']),
                'severity': 'warning',
                'pass_message': 'Data model directories found',
                'fail_message': 'No models/schemas/entities folders found'
            },
            {
                'name': 'has_config',
                'function': lambda: self._has_dir_matching(['config', 'settings', 'core']),
                'severity': 'info',
                'pass_message': 'Configuration directory found',
                'fail_message': 'No config/settings/core folder found'
            },
            {
                'name': 'has_middleware_services',
                'function': lambda: self._has_dir_matching(['middleware', 'services']),
                'severity': 'info',
                'pass_message': 'Middleware/services directory found',
                'fail_message': 'No middleware/services folders found'
            },
            {
                'name': 'has_entry_point',
                'function': lambda: self._has_file_matching(['app.', 'main.', 'server.']),
                'severity': 'warning',
                'pass_message': 'Entry point file found',
                'fail_message': 'No app.*/main.*/server.* file found'
            },
            {
                'name': 'has_db_files',
                'function': lambda: self._has_dir_matching(['migrations', 'prisma', 'alembic']),
                'severity': 'info',
                'pass_message': 'Database schema/migration files found',
                'fail_message': 'No migrations/prisma/alembic folders found'
            },
            {
                'name': 'has_env_config',
                'function': lambda: self._has_file_matching(['.env']),
                'severity': 'info',
                'pass_message': 'Environment config found',
                'fail_message': 'No .env files found'
            }
        ]
