import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import (
    CompetencyEvidenceState,
    CompetencyEvidenceType,
    CareerAlignmentStatus,
    CareerSkillGapType,
    CareerGapSeverity,
    CareerRecommendationType,
    CareerRecommendationStatus,
    ProjectVerificationStatus,
    RoleRequirementImportance,
    RoleMappingStatus,
    IndustryImportance,
)
from app.models.career import DEFAULT_CAREER_READINESS_DISCLAIMER


# =========================================================================
# 1. Role Profiles & Competency Requirements
# =========================================================================

class IndustryCompetencyRequirementBase(BaseModel):
    competency_name: str = Field(..., max_length=255)
    category: str = Field(default="PROGRAMMING", max_length=50)
    required_depth: int = Field(default=3, ge=1, le=5)
    importance: str = Field(default="HIGH", max_length=50)
    description: Optional[str] = None
    competency_id: Optional[uuid.UUID] = None
    mapping_status: str = Field(default="APPROVED", max_length=50)
    source_reference: Optional[str] = None
    rationale: Optional[str] = None


class IndustryCompetencyRequirementCreate(IndustryCompetencyRequirementBase):
    role_id: uuid.UUID


class IndustryCompetencyRequirementResponse(IndustryCompetencyRequirementBase):
    id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndustryRoleProfileBase(BaseModel):
    role_title: str = Field(..., max_length=255)
    role_family: str = Field(..., max_length=100)
    description: str
    experience_tier: str = Field(default="Entry-Level / Fresher", max_length=50)
    version: str = Field(default="1.0", max_length=50)
    is_active: bool = True
    review_status: str = Field(default="APPROVED", max_length=50)


class IndustryRoleProfileCreate(IndustryRoleProfileBase):
    institution_id: Optional[uuid.UUID] = None


class IndustryRoleProfileUpdate(BaseModel):
    role_title: Optional[str] = None
    role_family: Optional[str] = None
    description: Optional[str] = None
    experience_tier: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    review_status: Optional[str] = None


class IndustryRoleProfileResponse(IndustryRoleProfileBase):
    id: uuid.UUID
    institution_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    requirements: List[IndustryCompetencyRequirementResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 2. Student Project Evidence Schemas
# =========================================================================

class StudentProjectEvidenceBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    technology_stack: List[str] = Field(default_factory=list)
    repository_url: Optional[str] = Field(None, max_length=512)
    portfolio_url: Optional[str] = Field(None, max_length=512)
    documentation_url: Optional[str] = Field(None, max_length=512)
    demonstrated_competencies: List[str] = Field(default_factory=list)


class StudentProjectEvidenceCreate(StudentProjectEvidenceBase):
    student_id: Optional[uuid.UUID] = None  # If student submitting, inferred from auth profile


class StudentProjectEvidenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technology_stack: Optional[List[str]] = None
    repository_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    documentation_url: Optional[str] = None
    demonstrated_competencies: Optional[List[str]] = None


class StudentProjectEvidenceReview(BaseModel):
    verification_status: ProjectVerificationStatus
    verification_notes: Optional[str] = None


class StudentProjectEvidenceResponse(StudentProjectEvidenceBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    verification_status: str
    reviewer_id: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 3. Student Competency Evidence Schemas
# =========================================================================

class StudentCompetencyEvidenceBase(BaseModel):
    competency_name: str = Field(..., max_length=255)
    category: str = Field(default="PROGRAMMING", max_length=50)
    evidence_type: str = Field(default=CompetencyEvidenceType.THEORETICAL_ASSESSMENT.value)
    source_entity_type: str = Field(..., max_length=50)
    source_entity_id: Optional[uuid.UUID] = None
    evidence_state: str = Field(default=CompetencyEvidenceState.NOT_ASSESSED.value)
    score_or_metric: Optional[float] = None
    evidence_summary: str
    provenance_details: Dict[str, Any] = Field(default_factory=dict)
    is_eligible: bool = True
    exclusion_reason: Optional[str] = None


class StudentCompetencyEvidenceCreate(StudentCompetencyEvidenceBase):
    student_id: uuid.UUID
    competency_id: Optional[uuid.UUID] = None


class StudentCompetencyEvidenceResponse(StudentCompetencyEvidenceBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    competency_id: Optional[uuid.UUID] = None
    verified_by: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 4. Career Skill Gap Schemas
# =========================================================================

class CareerSkillGapFindingResponse(BaseModel):
    id: uuid.UUID
    analysis_id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    role_id: uuid.UUID
    requirement_id: Optional[uuid.UUID] = None
    competency_name: str
    importance: str
    gap_type: str
    current_evidence_state: str
    gap_severity: str
    rationale: str
    suggested_action: str
    evidence_needed: str
    related_subject_id: Optional[uuid.UUID] = None
    related_learning_outcome_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 5. Career Development Recommendations
# =========================================================================

class CareerDevelopmentRecommendationBase(BaseModel):
    title: str = Field(..., max_length=255)
    target_competency: str = Field(..., max_length=255)
    recommendation_type: str = Field(default=CareerRecommendationType.PRACTICAL_PROJECT.value)
    priority: str = Field(default=CareerGapSeverity.HIGH.value)
    action_plan: str
    expected_evidence: str
    estimated_duration_days: int = Field(default=14, ge=1, le=180)
    academic_intervention_plan_id: Optional[uuid.UUID] = None


class CareerDevelopmentRecommendationCreate(CareerDevelopmentRecommendationBase):
    student_id: uuid.UUID
    role_id: uuid.UUID
    analysis_id: Optional[uuid.UUID] = None
    gap_id: Optional[uuid.UUID] = None


class CareerDevelopmentRecommendationUpdate(BaseModel):
    status: Optional[str] = None
    student_notes: Optional[str] = None
    reviewer_feedback: Optional[str] = None


class CareerDevelopmentRecommendationResponse(CareerDevelopmentRecommendationBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    role_id: uuid.UUID
    analysis_id: Optional[uuid.UUID] = None
    gap_id: Optional[uuid.UUID] = None
    status: str
    student_notes: Optional[str] = None
    reviewer_feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 6. Career Readiness Analysis Schemas
# =========================================================================

class CareerReadinessAnalysisRequest(BaseModel):
    student_id: Optional[uuid.UUID] = None  # Inferred if student calling
    role_id: uuid.UUID
    force_recalculate: bool = False


class CareerReadinessAnalysisResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    role_id: uuid.UUID
    role_title: Optional[str] = None
    alignment_status: str
    total_requirements_count: int
    demonstrated_count: int
    developing_count: int
    insufficient_evidence_count: int
    not_assessed_count: int
    review_required_count: int
    core_competency_coverage: float
    practical_evidence_coverage: float
    faculty_reviewed_count: int
    summary_rationale: str
    disclaimer: str
    analysis_version: str
    created_at: datetime
    gap_findings: List[CareerSkillGapFindingResponse] = Field(default_factory=list)
    recommendations: List[CareerDevelopmentRecommendationResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoleComparisonItem(BaseModel):
    role_id: uuid.UUID
    role_title: str
    alignment_status: str
    total_requirements: int
    demonstrated_count: int
    developing_count: int
    gap_count: int
    core_coverage_pct: float
    practical_coverage_pct: float


class CareerReadinessComparisonResponse(BaseModel):
    student_id: uuid.UUID
    compared_roles: List[RoleComparisonItem] = Field(default_factory=list)
    disclaimer: str = DEFAULT_CAREER_READINESS_DISCLAIMER


class CareerDashboardOverviewResponse(BaseModel):
    student_id: uuid.UUID
    enrolled_roles_count: int
    latest_analysis: Optional[CareerReadinessAnalysisResponse] = None
    verified_projects_count: int
    pending_projects_count: int
    demonstrated_competencies_count: int
    developing_competencies_count: int
    active_gaps_count: int
    active_recommendations_count: int
    disclaimer: str = DEFAULT_CAREER_READINESS_DISCLAIMER
