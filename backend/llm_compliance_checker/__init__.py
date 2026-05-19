# llm_compliance_checker/__init__.py
"""
LLM-based compliance checker for repository directories.
"""

from .runner import check_dynamic, check_specific

__version__ = "0.1.0"

__all__ = ["check_dynamic", "check_specific"]
