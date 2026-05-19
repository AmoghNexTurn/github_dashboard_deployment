# repo_analyzer/prompt_builder.py (UPDATED)
"""
Prompt building functions for LLM analysis.
Calls data gatherers and builds analysis prompts.
"""

from typing import Optional, List
import json
from .data_gatherer import gather_comprehensive_data, gather_specific_data


def build_comprehensive_prompt(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[str]:
    """
    Build a comprehensive analysis prompt by gathering all data.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Prompt string for LLM or None if no data available
    """
    # Gather all data
    data = gather_comprehensive_data(repo_owner, repo_name, branch, github_pat)

    # Check if we have any analysis data
    if not data.get('analyses'):
        return None

    # Build compact summary for prompt
    repo_info = data['repository']
    analyses = data['analyses']

    summary = {
        'repository': f"{repo_info['owner']}/{repo_info['name']}",
        'branch': repo_info['branch'],
    }

    # Add compact key insights from each available analysis
    if 'readme' in analyses:
        pii_note = f" (PII redacted: {analyses['readme']['pii_detected']})" if analyses['readme']['pii_detected'] else ""
        summary['readme'] = {
            'path': analyses['readme']['path'],
            'size': analyses['readme']['size'],
            'preview': analyses['readme']['content'][:200],
            'pii_detected': analyses['readme']['pii_detected']
        }

    if 'dependencies' in analyses:
        summary['dependencies'] = [
            f"{f['ecosystem']}: {f['path']}"
            for f in analyses['dependencies']['files'][:5]  # Limit to 5
        ]

    if 'structure' in analyses:
        summary['structure'] = {
            'files': analyses['structure']['total_files'],
            'dirs': analyses['structure']['total_directories'],
            # Limit
            'root_dirs': analyses['structure']['root_directories'][:8],
            # Top 5
            'top_ext': dict(list(analyses['structure']['top_extensions'].items())[:5])
        }

    if 'naming' in analyses:
        summary['naming'] = {
            'file_patterns': analyses['naming']['file_naming']['patterns'],
            'dir_patterns': analyses['naming']['directory_naming']['patterns']
        }

    if 'git_metadata' in analyses:
        summary['git'] = {
            'commits': analyses['git_metadata']['recent_commits']['count'],
            'branches': analyses['git_metadata']['branches']['count'],
            'conventional': analyses['git_metadata']['recent_commits']['analysis']['uses_conventional_commits'],
            'language': analyses['git_metadata']['repository'].get('language'),
            'stars': analyses['git_metadata']['repository'].get('stars')
        }

    # Build compact prompt
    prompt = f"""Analyze this repository and provide insights in the exact JSON format specified.

Repository Data:
{json.dumps(summary, indent=2)}

Respond with a JSON object containing:
- overall_health_score: integer 1-10
- justification: string (brief, 1-2 sentences)
- strengths: array of exactly 3 strings
- improvements: array of exactly 3 strings
- technology_stack: string (brief assessment)
- recommended_next_steps: array of strings

Be concise and actionable."""

    return prompt


def build_specific_prompt(
    repo_owner: str,
    repo_name: str,
    branch: str,
    analysis_types: List[str],
    github_pat: Optional[str] = None
) -> Optional[str]:
    """
    Build a specific analysis prompt by gathering selected data types.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        analysis_types: List of analysis types to include
        github_pat: GitHub personal access token (optional)

    Returns:
        Prompt string for LLM or None if no data available
    """
    # Gather specific data
    data = gather_specific_data(
        repo_owner, repo_name, branch, analysis_types, github_pat)

    # Check if we have any analysis data
    if not data.get('analyses'):
        return None

    repo_info = data['repository']
    analyses = data['analyses']

    # Build focused prompt based on requested analyses
    prompt_parts = [
        f"Analyze the following aspects of repository {repo_info['owner']}/{repo_info['name']}.",
        "Respond with a JSON object containing the requested analyses.\n"
    ]

    if 'readme' in analyses:
        readme = analyses['readme']
        pii_note = f"\nNote: The following PII types were detected and redacted: {readme['pii_detected']}" if readme[
            'pii_detected'] else ""
        prompt_parts.append(f"""README Analysis (content size: {readme['size']} bytes):
{readme['content'][:500]}

Provide:
- missing_sections: array of strings
- quality_score: integer 1-10
- justification: string (brief)
- top_improvements: array of exactly 3 strings
- pii_detected: {json.dumps(readme['pii_detected'])}

IMPORTANT: pii_detected must be exactly {json.dumps(readme['pii_detected'])} in your response.
""")

    if 'dependencies' in analyses:
        # Only include basic info, not full content
        deps_summary = []
        for f in analyses['dependencies']['files'][:5]:  # Limit to 5 files
            # Extract just package names from content, not full content
            deps_summary.append({
                'path': f['path'],
                'ecosystem': f['ecosystem']
            })

        prompt_parts.append(f"""Dependency Analysis:
Dependency files found: {json.dumps(deps_summary, indent=2)}

Provide:
- conflicts: array of strings (e.g., "mixing npm and yarn")
- security_concerns: array of strings (general concerns based on ecosystem)
- optimizations: array of strings (e.g., "consider using lock files")
""")

    if 'structure' in analyses:
        struct = analyses['structure']
        struct_summary = {
            'files': struct['total_files'],
            'dirs': struct['total_directories'],
            'root': struct['root_directories'][:8],
            'extensions': dict(list(struct['top_extensions'].items())[:5])
        }
        prompt_parts.append(f"""Structure Analysis:
{json.dumps(struct_summary, indent=2)}

Provide:
- project_type: string
- missing_items: array of strings
- suggestions: array of strings
- red_flags: array of strings
""")

    if 'naming' in analyses:
        naming = analyses['naming']
        prompt_parts.append(f"""Naming Convention Analysis:
File patterns: {naming['file_naming']['patterns']}
Dir patterns: {naming['directory_naming']['patterns']}

Provide:
- consistency_score: integer 1-10
- dominant_convention: string
- inconsistencies: array of strings
- recommendation: string
""")

    if 'git_metadata' in analyses:
        git = analyses['git_metadata']
        git_summary = {
            'commits': git['recent_commits']['count'],
            'conventional': git['recent_commits']['analysis']['uses_conventional_commits'],
            'branches': git['branches']['count']
        }
        prompt_parts.append(f"""Git Metadata Analysis:
{json.dumps(git_summary, indent=2)}

Provide:
- commit_quality: string
- branching_strategy: string
- activity_insights: string
- recommendations: array of strings
""")

    prompt_parts.append("\nBe concise and actionable in all responses.")

    return "\n".join(prompt_parts)
