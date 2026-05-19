# checks/frontend.py
"""
Frontend directory checker.
"""

from typing import List, Dict, Any
from .base import BaseChecker


class FrontendChecker(BaseChecker):
    """Checker for frontend directories."""

    def get_checks(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'has_package_json',
                'function': lambda: self._has_file_matching(['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']),
                'severity': 'error',
                'pass_message': 'Package manifest found',
                'fail_message': 'No package.json or lockfile found'
            },
            {
                'name': 'has_src_folder',
                'function': lambda: self._has_dir_matching(['src']),
                'severity': 'warning',
                'pass_message': 'Source folder found',
                'fail_message': 'No src/ folder found'
            },
            {
                'name': 'has_static_assets',
                'function': lambda: self._has_dir_matching(['public', 'assets', 'static']),
                'severity': 'info',
                'pass_message': 'Static assets folder found',
                'fail_message': 'No static assets folder found'
            },
            {
                'name': 'has_entry_file',
                'function': lambda: self._has_file_matching(['index.', 'main.', 'App.']),
                'severity': 'warning',
                'pass_message': 'Entry file found',
                'fail_message': 'No entry file (index.*, main.*, App.*) found'
            },
            {
                'name': 'has_build_config',
                'function': lambda: self._has_file_matching(['vite.config.', 'webpack.config.', 'next.config.']),
                'severity': 'info',
                'pass_message': 'Build configuration found',
                'fail_message': 'No build config found'
            },
            {
                'name': 'has_ui_folders',
                'function': lambda: self._has_dir_matching(['components', 'pages', 'views']),
                'severity': 'warning',
                'pass_message': 'UI component folders found',
                'fail_message': 'No component/page/view folders found'
            },
            {
                'name': 'has_styles',
                'function': lambda: self._has_item_matching(['styles', '.css', '.scss', '.sass', '.less']),
                'severity': 'info',
                'pass_message': 'Style files or folder found',
                'fail_message': 'No styles folder or CSS files found'
            },
            {
                'name': 'has_lint_config',
                'function': lambda: self._has_file_matching(['.eslintrc', 'eslint.config.', '.prettierrc', 'prettier.config.']),
                'severity': 'info',
                'pass_message': 'Linting configuration found',
                'fail_message': 'No lint config files found'
            }
        ]
