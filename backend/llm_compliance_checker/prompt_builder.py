# llm_compliance_checker/prompt_builder.py
"""
Build prompts for LLM compliance checking.
"""
from typing import List, Dict, Optional
import json
from .checklist_definitions import CHECKLISTS


def build_check_prompt(
    files: List[str],
    directories: List[str],
    category: str,
    selected_checks: Optional[Dict[int, bool]] = None
) -> str:
    """
    Build prompt for LLM to evaluate compliance checks.

    Args:
        files: List of file paths
        directories: List of directory paths
        category: Category type (frontend, backend, etc.)
        selected_checks: Optional dict of which checks to run (1-based indexing)

    Returns:
        Prompt string
    """
    checklist = CHECKLISTS[category]

    # Filter checks if selection provided
    if selected_checks is not None:
        checklist = [
            check for idx, check in enumerate(checklist, 1)
            if selected_checks.get(idx, False)
        ]

    # Build check list for prompt
    check_descriptions = []
    for idx, check in enumerate(checklist, 1):
        check_descriptions.append(
            f"{idx}. {check['name']}: {check['description']} (severity: {check['severity']})"
        )

    prompt = f"""You are analyzing a {category} directory structure.

Files in directory:
{json.dumps(files[:100], indent=2)}

Directories in directory:
{json.dumps(directories[:50], indent=2)}

Evaluate these compliance checks:
{chr(10).join(check_descriptions)}

For each check, determine if it PASSED or FAILED based on the files and directories present.

Respond with a JSON object with this EXACT structure:
{{
  "results": [
    {{
      "check": "<check_name>",
      "passed": <true/false>,
      "message": "<brief message>",
      "severity": "<error/warning/info>"
    }}
  ]
}}

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks, no explanations."""

    return prompt
