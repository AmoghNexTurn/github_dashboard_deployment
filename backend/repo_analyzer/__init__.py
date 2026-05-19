# repo_analyzer/__init__.py (UPDATED)
"""
repo_analyzer - A tool for analyzing GitHub repositories to extract data for LLM analysis.

This module provides functionality to recursively search repositories and extract
various types of data including READMEs, dependencies, structure, naming conventions,
and git metadata, then build prompts for LLM analysis.
"""

from .prompt_builder import (
    build_comprehensive_prompt,
    build_specific_prompt
)
from .llm_analyzer import (
    analyze_comprehensive,
    analyze_specific
)
from .models import (
    ComprehensiveAnalysis,
    SpecificAnalysis,
    ReadmeAnalysis,
    DependencyAnalysis,
    StructureAnalysis,
    NamingAnalysis,
    GitMetadataAnalysis
)

__version__ = "0.1.0"

__all__ = [
    "build_comprehensive_prompt",
    "build_specific_prompt",
    "analyze_comprehensive",
    "analyze_specific",
    "ComprehensiveAnalysis",
    "SpecificAnalysis",
    "ReadmeAnalysis",
    "DependencyAnalysis",
    "StructureAnalysis",
    "NamingAnalysis",
    "GitMetadataAnalysis"
]
