"""
compliance_checker - A tool for analyzing and scoring repository directory structures.

This module provides functionality to classify repository directories and check
them against standard conventions for different project types (frontend, backend,
infrastructure, shared, docs).
"""

from .classifier import classify_directory
from .runner import dynamic_checklist, specific_checklist

__version__ = "0.1.0"

__all__ = [
    "classify_directory",
    "dynamic_checklist",
    "specific_checklist",
]
