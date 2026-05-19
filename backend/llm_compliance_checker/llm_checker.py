# llm_compliance_checker/llm_checker.py
"""
LLM-based compliance checking.
"""

from typing import List, Dict, Optional
import os
import json
from .models import ComplianceReport, CheckResult
from .prompt_builder import build_check_prompt
from .checklist_definitions import CHECKLISTS
from pydantic import SecretStr, ValidationError
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq


def check_with_llm(
    files: List[str],
    directories: List[str],
    category: str,
    url: str,
    selected_checks: Optional[Dict[int, bool]] = None,
    groq_api_key: Optional[str] = None
) -> Dict:
    """
    Check directory compliance using LLM.

    Args:
        files: List of file paths
        directories: List of directory paths
        category: Category type
        url: API URL for the directory
        selected_checks: Optional dict of which checks to run
        groq_api_key: Groq API key

    Returns:
        Compliance report dict
    """
    # Get API key
    api_key = groq_api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "Groq API key not provided and GROQ_API_KEY environment variable not set")

    # Build prompt
    prompt = build_check_prompt(files, directories, category, selected_checks)

    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key),
        temperature=0.1
    )

    # Invoke LLM
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    # Extract and clean content
    content = response.content
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)

    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Parse JSON
    try:
        parsed = json.loads(content)
        results = [CheckResult(**r) for r in parsed['results']]
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        raise ValueError(
            f"Failed to parse LLM response: {e}\nResponse: {content}")

    # Calculate stats
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    # Build report
    report = ComplianceReport(
        category=category,
        url=url,
        total_checks=len(results),
        passed=passed,
        failed=failed,
        results=results
    )

    return {"report": report.model_dump()}
