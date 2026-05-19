# checks/base.py
"""
Base checker class for all directory type checkers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseChecker(ABC):
    """Base class for directory type checkers."""

    def __init__(self, files: List[str], directories: List[str]):
        """
        Initialize checker with directory contents.

        Args:
            files: List of file paths (can be nested like 'src/index.js')
            directories: List of directory paths (can be nested like 'src/components')
        """
        self.files = files
        self.directories = directories
        self.all_items = files + directories

    @abstractmethod
    def get_checks(self) -> List[Dict[str, Any]]:
        """
        Return list of check definitions.

        Returns:
            List of dicts with keys: 'name', 'function', 'severity', 'description'
        """
        pass

    def run_checks(self, selected_checks: Optional[Dict[int, bool]] = None) -> List[Dict[str, Any]]:
        """
        Run checks and return results.

        Args:
            selected_checks: Optional dict mapping check index (1-based) to bool
                           If None, all checks are run

        Returns:
            List of check results
        """
        checks = self.get_checks()
        results = []

        for idx, check in enumerate(checks, start=1):
            # Skip if this check is disabled
            if selected_checks is not None and not selected_checks.get(idx, False):
                continue

            # Run the check function
            passed = check['function']()

            results.append({
                'check': check['name'],
                'passed': passed,
                'message': check['pass_message'] if passed else check['fail_message'],
                'severity': check['severity']
            })

        return results

    def _has_file_matching(self, patterns: List[str]) -> bool:
        """Check if any file matches the given patterns (handles nested paths)."""
        for file_path in self.files:
            # Get just the filename from the path
            filename = file_path.split('/')[-1].lower()
            # Also check the full path
            full_path_lower = file_path.lower()

            for pattern in patterns:
                pattern_lower = pattern.lower()
                # Check if pattern matches filename or is in the path
                if (pattern_lower in filename or
                    filename.startswith(pattern_lower) or
                    filename.endswith(pattern_lower) or
                        pattern_lower in full_path_lower):
                    return True
        return False

    def _has_dir_matching(self, patterns: List[str]) -> bool:
        """Check if any directory matches the given patterns (handles nested paths)."""
        for dir_path in self.directories:
            # Check each part of the path
            path_parts = dir_path.lower().split('/')

            for pattern in patterns:
                pattern_lower = pattern.lower()
                # Check if pattern matches any part of the path or the full dirname
                dirname = path_parts[-1]
                if (pattern_lower in dirname or
                    dirname == pattern_lower or
                        pattern_lower in dir_path.lower()):
                    return True
        return False

    def _has_item_matching(self, patterns: List[str]) -> bool:
        """Check if any file or directory matches the given patterns."""
        return self._has_file_matching(patterns) or self._has_dir_matching(patterns)
