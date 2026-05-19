# repo_analyzer/models.py (UPDATE ReadmeAnalysis only)
"""
Pydantic models for LLM output validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ComprehensiveAnalysis(BaseModel):
    """Model for comprehensive repository analysis."""
    overall_health_score: int = Field(..., ge=1,
                                      le=10, description="Score from 1-10")
    justification: str = Field(...,
                               description="Brief justification for the score")
    strengths: List[str] = Field(..., min_length=3,
                                 max_length=3, description="Top 3 strengths")
    improvements: List[str] = Field(..., min_length=3,
                                    max_length=3, description="Top 3 improvements")
    technology_stack: str = Field(...,
                                  description="Brief technology stack assessment")
    recommended_next_steps: List[str] = Field(
        ..., description="Recommended next steps")


class ReadmeAnalysis(BaseModel):
    """Model for README analysis."""
    missing_sections: List[str] = Field(...,
                                        description="List of missing sections")
    quality_score: int = Field(..., ge=1, le=10,
                               description="Quality score from 1-10")
    justification: str = Field(...,
                               description="Brief justification for score")
    top_improvements: List[str] = Field(..., min_length=3,
                                        max_length=3, description="Top 3 improvements")
    pii_detected: List[str] = Field(...,
                                    description="List of PII types detected and redacted")


class DependencyAnalysis(BaseModel):
    """Model for dependency analysis."""
    conflicts: List[str] = Field(...,
                                 description="Conflicting or unusual dependencies")
    security_concerns: List[str] = Field(..., description="Security concerns")
    optimizations: List[str] = Field(...,
                                     description="Optimization suggestions")


class StructureAnalysis(BaseModel):
    """Model for structure analysis."""
    project_type: str = Field(..., description="Identified project type")
    missing_items: List[str] = Field(...,
                                     description="Missing standard directories/files")
    suggestions: List[str] = Field(...,
                                   description="Organizational improvements")
    red_flags: List[str] = Field(..., description="Red flags or anti-patterns")


class NamingAnalysis(BaseModel):
    """Model for naming convention analysis."""
    consistency_score: int = Field(..., ge=1, le=10,
                                   description="Consistency score from 1-10")
    dominant_convention: str = Field(...,
                                     description="Dominant naming convention")
    inconsistencies: List[str] = Field(...,
                                       description="Naming inconsistencies")
    recommendation: str = Field(...,
                                description="Standardization recommendation")


class GitMetadataAnalysis(BaseModel):
    """Model for git metadata analysis."""
    commit_quality: str = Field(...,
                                description="Commit message quality assessment")
    branching_strategy: str = Field(...,
                                    description="Branching strategy observation")
    activity_insights: str = Field(...,
                                   description="Development activity insights")
    recommendations: List[str] = Field(...,
                                       description="Improvement recommendations")


class SpecificAnalysis(BaseModel):
    """Model for specific analysis combining requested types."""
    readme: Optional[ReadmeAnalysis] = None
    dependencies: Optional[DependencyAnalysis] = None
    structure: Optional[StructureAnalysis] = None
    naming: Optional[NamingAnalysis] = None
    git_metadata: Optional[GitMetadataAnalysis] = None
