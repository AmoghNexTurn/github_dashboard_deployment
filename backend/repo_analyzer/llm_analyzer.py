# repo_analyzer/llm_analyzer.py (COMPLETE REWRITE)
"""
LLM analysis using LangChain and Groq with structured output.
"""

from typing import Optional, List
import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from pydantic import SecretStr, ValidationError
from .prompt_builder import build_comprehensive_prompt, build_specific_prompt
from .models import ComprehensiveAnalysis, SpecificAnalysis


def analyze_comprehensive(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None,
    groq_api_key: Optional[str] = None
) -> Optional[ComprehensiveAnalysis]:
    """
    Perform comprehensive LLM analysis of a repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)
        groq_api_key: Groq API key (optional, will use GROQ_API_KEY env var if not provided)

    Returns:
        ComprehensiveAnalysis model or None if prompt building failed
    """
    # Build the prompt
    prompt = build_comprehensive_prompt(
        repo_owner, repo_name, branch, github_pat)

    if not prompt:
        return None

    # Get Groq API key
    api_key = groq_api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "Groq API key not provided and GROQ_API_KEY environment variable not set")

    # Initialize LangChain Groq
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key),
        temperature=0.1
    )

    # Add explicit JSON instruction to prompt
    json_prompt = f"""{prompt}

CRITICAL: Respond ONLY with a valid JSON object. No markdown, no code blocks, no explanations.
The JSON must match this exact structure:
{{
  "overall_health_score": <number 1-10>,
  "justification": "<string>",
  "strengths": ["<string>", "<string>", "<string>"],
  "improvements": ["<string>", "<string>", "<string>"],
  "technology_stack": "<string>",
  "recommended_next_steps": ["<string>", ...]
}}"""

    # Invoke LLM
    messages = [HumanMessage(content=json_prompt)]
    response = llm.invoke(messages)

    # Extract content
    content = response.content
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)

    # Clean the response - remove markdown code blocks if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Parse JSON and validate
    try:
        parsed = json.loads(content)
        return ComprehensiveAnalysis(**parsed)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(
            f"Failed to parse LLM response as valid JSON: {e}\nResponse: {content}")


def analyze_specific(
    repo_owner: str,
    repo_name: str,
    branch: str,
    analysis_types: List[str],
    github_pat: Optional[str] = None,
    groq_api_key: Optional[str] = None
) -> Optional[SpecificAnalysis]:
    """
    Perform specific LLM analysis of a repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        analysis_types: List of analysis types to include
        github_pat: GitHub personal access token (optional)
        groq_api_key: Groq API key (optional, will use GROQ_API_KEY env var if not provided)

    Returns:
        SpecificAnalysis model or None if prompt building failed
    """
    # Build the prompt
    prompt = build_specific_prompt(
        repo_owner, repo_name, branch, analysis_types, github_pat)

    if not prompt:
        return None
    print(prompt)

    # Get Groq API key
    api_key = groq_api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "Groq API key not provided and GROQ_API_KEY environment variable not set")

    # Initialize LangChain Groq
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(api_key),
        temperature=0.1
    )

    # Build JSON schema instruction based on requested types
    schema_parts = []

    if 'readme' in analysis_types:
        schema_parts.append(
            '"readme": {"missing_sections": [...], "quality_score": <1-10>, "justification": "...", "top_improvements": [...], "pii_detected": [...]}')

    if 'dependencies' in analysis_types:
        schema_parts.append(
            '"dependencies": {"conflicts": [...], "security_concerns": [...], "optimizations": [...]}')

    if 'structure' in analysis_types:
        schema_parts.append(
            '"structure": {"project_type": "...", "missing_items": [...], "suggestions": [...], "red_flags": [...]}')

    if 'naming' in analysis_types:
        schema_parts.append(
            '"naming": {"consistency_score": <1-10>, "dominant_convention": "...", "inconsistencies": [...], "recommendation": "..."}')

    if 'git_metadata' in analysis_types:
        schema_parts.append(
            '"git_metadata": {"commit_quality": "...", "branching_strategy": "...", "activity_insights": "...", "recommendations": [...]}')

    schema = "{" + ", ".join(schema_parts) + "}"

    # Add explicit JSON instruction to prompt
    json_prompt = f"""{prompt}

CRITICAL: Respond ONLY with a valid JSON object. No markdown, no code blocks, no explanations.
The JSON must match this exact structure:
{schema}"""

    # Invoke LLM
    messages = [HumanMessage(content=json_prompt)]
    response = llm.invoke(messages)

    # Extract content
    content = response.content
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)

    # Clean the response - remove markdown code blocks if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Parse JSON and validate
    try:
        parsed = json.loads(content)
        return SpecificAnalysis(**parsed)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(
            f"Failed to parse LLM response as valid JSON: {e}\nResponse: {content}")
