import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import (
    InterventionType,
    InterventionPriority,
    InterventionPlanStatus,
    InterventionActionStatus,
    InterventionRecommendationStatus,
    InterventionEventType,
    EvidenceSufficiencyLevel,
)
from app.models.interventions import DEFAULT_INTERVENTION_DISCLAIMER


# =========================================================================
# 1. Template Schemas
# =========================================================================

class InterventionTemplateBase(BaseModel):
    template_code: str = Field(..., max_length=64, description="Unique institutional template code")
    template_name: str = Field(..., max_length=255, description="Descriptive template title")
    intervention_type: InterventionType = Field(default=InterventionType.TARGETED_REVISION)
    description: Optional[str] = None
    target_level: str = Field(default="TOPIC", description="Target scope: TOPIC, UNIT, CLO, SUBJECT")
    suggested_duration_hours: float = Field(default=2.0, ge=0.5, le=100.0)
    suggested_completion_days: int = Field(default=7, ge=1, le=90)
    recommended_actions_template: List[Dict[str, Any]] = Field(default_factory=list)
    required_resources: List[Dict[str, Any]] = Field(default_factory=list)
    expected_evidence_type: Optional[str] = None
    requires_faculty_review: bool = True
    is_active: bool = True


class InterventionTemplateCreate(InterventionTemplateBase):
    subject_id: Optional[uuid.UUID] = None


class InterventionTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    suggested_duration_hours: Optional[float] = None
    suggested_completion_days: Optional[int] = None
    recommended_actions_template: Optional[List[Dict[str, Any]]] = None
    required_resources: Optional[List[Dict[str, Any]]] = None
    expected_evidence_type: Optional[str] = None
    requires_faculty_review: Optional[bool] = None
    is_active: Optional[bool] = None


class InterventionTemplateResponse(InterventionTemplateBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: Optional[uuid.UUID] = None
    created_by_profile_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 2. Recommendation Schemas
# =========================================================================

class InterventionRecommendationGenerateRequest(BaseModel):
    student_id: uuid.UUID
    subject_id: uuid.UUID
    topic_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None


class BatchRecommendationGenerateRequest(BaseModel):
    subject_id: uuid.UUID
    target_id: Optional[uuid.UUID] = None


class InterventionRecommendationResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    enrollment_number: Optional[str] = None
    subject_id: uuid.UUID
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    topic_id: Optional[uuid.UUID] = None
    topic_name: Optional[str] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    risk_prediction_id: Optional[uuid.UUID] = None
    learning_gap_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    recommendation_type: str
    priority: str
    rationale: str
    source_evidence_summary: Dict[str, Any]
    evidence_sufficiency: str
    proposed_action_title: str
    proposed_action_description: str
    suggested_duration_days: int
    status: str
    scientific_disclaimer: str = DEFAULT_INTERVENTION_DISCLAIMER
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 3. Action Schemas
# =========================================================================

class InterventionActionCreate(BaseModel):
    action_title: str = Field(..., max_length=255)
    action_type: InterventionType = Field(default=InterventionType.TARGETED_REVISION)
    instructions: str
    resource_references: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_effort_hours: float = Field(default=1.0, ge=0.25, le=40.0)
    due_date: Optional[datetime] = None


class InterventionActionStatusUpdate(BaseModel):
    new_status: InterventionActionStatus
    student_completion_notes: Optional[str] = None
    student_submission_url: Optional[str] = None
    faculty_feedback: Optional[str] = None


class InterventionActionResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    plan_id: uuid.UUID
    action_order: int
    action_title: str
    action_type: str
    instructions: str
    resource_references: List[Dict[str, Any]]
    estimated_effort_hours: float
    due_date: Optional[datetime] = None
    action_status: str
    student_completion_notes: Optional[str] = None
    student_submission_url: Optional[str] = None
    submitted_at: Optional[datetime] = None
    faculty_feedback: Optional[str] = None
    verified_by_faculty_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 4. Progress Event Schemas
# =========================================================================

class InterventionProgressEventResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    plan_id: uuid.UUID
    action_id: Optional[uuid.UUID] = None
    actor_profile_id: Optional[uuid.UUID] = None
    actor_name: Optional[str] = None
    event_type: str
    previous_status: Optional[str] = None
    new_status: str
    event_notes: Optional[str] = None
    event_metadata: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 5. Plan Schemas
# =========================================================================

class InterventionPlanCreate(BaseModel):
    student_id: uuid.UUID
    subject_id: uuid.UUID
    topic_id: Optional[uuid.UUID] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    recommendation_id: Optional[uuid.UUID] = None
    plan_title: str = Field(..., max_length=255)
    learning_objective: str
    assigned_faculty_id: Optional[uuid.UUID] = None
    target_completion_date: Optional[datetime] = None
    expected_outcome_evidence: Optional[str] = None
    initial_actions: Optional[List[InterventionActionCreate]] = None


class InterventionPlanUpdate(BaseModel):
    plan_title: Optional[str] = None
    learning_objective: Optional[str] = None
    target_completion_date: Optional[datetime] = None
    expected_outcome_evidence: Optional[str] = None
    assigned_faculty_id: Optional[uuid.UUID] = None


class InterventionPlanReviewRequest(BaseModel):
    decision: str = Field(..., description="APPROVE or REJECT")
    review_notes: Optional[str] = None
    assigned_faculty_id: Optional[uuid.UUID] = None


class AcademicInterventionPlanResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    enrollment_number: Optional[str] = None
    subject_id: uuid.UUID
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    topic_id: Optional[uuid.UUID] = None
    topic_name: Optional[str] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    recommendation_id: Optional[uuid.UUID] = None
    plan_title: str
    learning_objective: str
    plan_status: str
    assigned_faculty_id: Optional[uuid.UUID] = None
    assigned_faculty_name: Optional[str] = None
    reviewed_by_faculty_id: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    faculty_review_notes: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    expected_outcome_evidence: Optional[str] = None
    scientific_disclaimer: str = DEFAULT_INTERVENTION_DISCLAIMER
    created_at: datetime
    updated_at: datetime
    actions: List[InterventionActionResponse] = Field(default_factory=list)
    progress_events: List[InterventionProgressEventResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 6. Outcome Schemas
# =========================================================================

class InterventionOutcomeCreate(BaseModel):
    baseline_mastery_percentage: Optional[float] = None
    followup_assessment_id: Optional[uuid.UUID] = None
    followup_score_obtained: Optional[float] = None
    followup_maximum_marks: Optional[float] = None
    followup_mastery_percentage: Optional[float] = None
    observation_notes: Optional[str] = None


class InterventionOutcomeResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    plan_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    topic_id: Optional[uuid.UUID] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    baseline_mastery_percentage: Optional[float] = None
    followup_assessment_id: Optional[uuid.UUID] = None
    followup_score_obtained: Optional[float] = None
    followup_maximum_marks: Optional[float] = None
    followup_mastery_percentage: Optional[float] = None
    observation_notes: Optional[str] = None
    scientific_disclaimer: str = DEFAULT_INTERVENTION_DISCLAIMER
    observed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 7. Dashboard & Overview Schemas
# =========================================================================

class InterventionFacultyDashboardResponse(BaseModel):
    total_plans: int
    active_plans_count: int
    draft_review_count: int
    approved_assigned_count: int
    completed_plans_count: int
    overdue_actions_count: int
    insufficient_evidence_recommendations_count: int
    recent_plans: List[AcademicInterventionPlanResponse] = Field(default_factory=list)
    active_recommendations: List[InterventionRecommendationResponse] = Field(default_factory=list)
    scientific_disclaimer: str = DEFAULT_INTERVENTION_DISCLAIMER


class InterventionStudentWorkspaceResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    active_plans: List[AcademicInterventionPlanResponse] = Field(default_factory=list)
    pending_actions_count: int
    completed_actions_count: int
    scientific_disclaimer: str = DEFAULT_INTERVENTION_DISCLAIMER
