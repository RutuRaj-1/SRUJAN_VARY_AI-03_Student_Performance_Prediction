import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import (
    EvidenceSufficiencyLevel,
    ConfidenceCategory,
    MasteryStatus,
    AttainmentStatus,
    LearningGapType,
    LearningGapSeverity,
    AnalysisJobStatus,
    EvidenceEligibilityStatus,
    EvidenceExclusionReason,
)


class MasteryAnalyzeRequest(BaseModel):
    subject_id: uuid.UUID
    student_id: Optional[uuid.UUID] = None  # None = analyze all enrolled students
    academic_year: str = "2024-2025"
    semester: int = 4
    calculation_version: str = "v1.0-deterministic"
    include_practice_tests: bool = False


class MasteryJobResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: uuid.UUID
    student_id: Optional[uuid.UUID] = None
    academic_year: str
    semester: int
    curriculum_version: Optional[str] = None
    calculation_version: str
    status: str
    total_evidence_examined: int
    eligible_evidence_count: int
    excluded_evidence_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicMasteryDetailResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    topic_name: str
    unit_number: Optional[int] = None
    unit_title: Optional[str] = None
    eligible_question_count: int
    eligible_attempt_count: int
    marks_obtained: float
    maximum_marks: float
    mastery_percentage: Optional[float] = None
    evidence_sufficiency: str
    confidence_category: str
    mastery_status: str
    calculation_version: str
    calculated_at: datetime
    plain_explanation: str

    model_config = ConfigDict(from_attributes=True)


class LearningOutcomeAttainmentDetailResponse(BaseModel):
    id: uuid.UUID
    learning_outcome_id: uuid.UUID
    outcome_code: str
    description: str
    bloom_level: str
    eligible_question_count: int
    mapped_marks: float
    marks_obtained: float
    attainment_percentage: Optional[float] = None
    evidence_sufficiency: str
    confidence_category: str
    attainment_status: str
    calculation_version: str
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningGapFindingResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    topic_id: Optional[uuid.UUID] = None
    topic_name: Optional[str] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    outcome_code: Optional[str] = None
    finding_type: str
    severity: str
    evidence_summary: str
    supporting_evidence_refs: Optional[Dict[str, Any]] = None
    recommended_review_action: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MasteryEvidenceItemResponse(BaseModel):
    id: uuid.UUID
    source_entity_type: str
    source_entity_id: uuid.UUID
    assessment_id: Optional[uuid.UUID] = None
    assessment_name: Optional[str] = None
    question_id: Optional[uuid.UUID] = None
    question_text: Optional[str] = None
    marks_obtained: float
    maximum_marks: float
    eligibility_status: str
    exclusion_reason: Optional[str] = None
    mapping_status: str
    evaluation_status: str
    verification_status: Optional[str] = None
    bloom_level: Optional[str] = None
    is_practice_assessment: bool
    evidence_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentMasteryProfileResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    subject_id: uuid.UUID
    subject_name: str
    subject_code: str
    overall_mastery_percentage: Optional[float] = None
    total_topics_analyzed: int
    mastered_topics_count: int
    progressing_topics_count: int
    needs_attention_topics_count: int
    insufficient_evidence_topics_count: int
    topic_results: List[TopicMasteryDetailResponse]
    outcome_results: List[LearningOutcomeAttainmentDetailResponse]
    learning_gaps: List[LearningGapFindingResponse]
    cognitive_breakdown: Dict[str, Dict[str, Any]]
    competency_breakdown: Dict[str, Dict[str, Any]]
    evidence_sufficiency_summary: Dict[str, int]
    scientific_disclaimer: str


class PerformanceTrendPoint(BaseModel):
    timestamp: datetime
    assessment_name: str
    topic_id: Optional[uuid.UUID] = None
    topic_name: Optional[str] = None
    percentage: float
    evidence_type: str
    is_official: bool


class StudentPerformanceTrendResponse(BaseModel):
    student_id: uuid.UUID
    subject_id: uuid.UUID
    timeline: List[PerformanceTrendPoint]
    trend_direction: str  # IMPROVING, STABLE, DECLINING, INSUFFICIENT_OBSERVATIONS
    observation_count: int
    scientific_disclaimer: str


class CohortMasterySummaryResponse(BaseModel):
    subject_id: uuid.UUID
    subject_name: str
    subject_code: str
    total_students_enrolled: int
    students_analyzed: int
    topic_aggregates: List[Dict[str, Any]]
    outcome_aggregates: List[Dict[str, Any]]
    curriculum_coverage_percentage: float
    scientific_disclaimer: str
