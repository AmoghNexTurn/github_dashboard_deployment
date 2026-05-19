# llm_compliance_checker/models.py
"""
Pydantic models for LLM compliance check output.
"""

from pydantic import BaseModel, Field
from typing import List


class CheckResult(BaseModel):
    """Individual check result."""
    check: str
    passed: bool
    message: str
    severity: str


class ComplianceReport(BaseModel):
    """Complete compliance report."""
    category: str
    url: str
    total_checks: int
    passed: int
    failed: int
    results: List[CheckResult]
