import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import (
    AssessmentType,
    QuestionType,
    QuestionDifficulty,
    QuestionEvaluationMethod,
    AttemptStatus,
    ResponseEvaluationStatus,
    LearningEngagementEventType,
    AssessmentOnlineStatus,
    AssessmentEvaluationMode,
)


# ==========================================================
# Question Options Schemas
# ==========================================================

class QuestionOptionBase(BaseModel):
    option_text: str = Field(..., min_length=1)
    display_order: int = Field(default=1, ge=1)
    is_correct: bool = Field(default=False)
    explanation: Optional[str] = None


class QuestionOptionCreate(QuestionOptionBase):
    pass


class QuestionOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID
    option_text: str
    display_order: int
    is_correct: Optional[bool] = None  # Hidden for student taking assessment
    explanation: Optional[str] = None


class StudentQuestionOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    option_text: str
    display_order: int


# ==========================================================
# Question Bank Schemas
# ==========================================================

class QuestionBase(BaseModel):
    subject_id: uuid.UUID
    unit_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    competency_id: Optional[uuid.UUID] = None
    question_text: str = Field(..., min_length=3)
    question_type: QuestionType = QuestionType.MCQ
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    bloom_level: Optional[str] = None
    default_marks: float = Field(default=1.0, gt=0)
    explanation: Optional[str] = None
    expected_answer: Optional[str] = None
    evaluation_method: QuestionEvaluationMethod = QuestionEvaluationMethod.AUTOMATIC
    code_language: Optional[str] = None
    code_template: Optional[str] = None
    code_test_cases: Optional[List[Dict[str, Any]]] = None


class QuestionCreate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = None


class QuestionUpdate(BaseModel):
    unit_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    competency_id: Optional[uuid.UUID] = None
    question_text: Optional[str] = Field(None, min_length=3)
    difficulty: Optional[QuestionDifficulty] = None
    bloom_level: Optional[str] = None
    default_marks: Optional[float] = Field(None, gt=0)
    explanation: Optional[str] = None
    expected_answer: Optional[str] = None
    evaluation_method: Optional[QuestionEvaluationMethod] = None
    verification_status: Optional[str] = None
    options: Optional[List[QuestionOptionCreate]] = None


class QuestionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: uuid.UUID
    unit_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    learning_outcome_id: Optional[uuid.UUID] = None
    competency_id: Optional[uuid.UUID] = None
    question_text: str
    question_type: str
    difficulty: str
    bloom_level: Optional[str] = None
    default_marks: float
    explanation: Optional[str] = None
    expected_answer: Optional[str] = None
    evaluation_method: str
    code_language: Optional[str] = None
    code_template: Optional[str] = None
    code_test_cases: Optional[List[Dict[str, Any]]] = None
    verification_status: str
    version: int
    created_at: datetime
    updated_at: datetime
    options: List[QuestionOptionResponse] = []


class StudentQuestionView(BaseModel):
    """Secure question representation for students actively attempting an assessment."""
    id: uuid.UUID
    question_text: str
    question_type: str
    marks_allocated: float
    display_order: int
    required: bool
    code_language: Optional[str] = None
    code_template: Optional[str] = None
    options: List[StudentQuestionOptionResponse] = []


# ==========================================================
# Assessment Creation & Configuration Schemas
# ==========================================================

class QuestionMappingItem(BaseModel):
    question_id: uuid.UUID
    marks_allocated: float = Field(..., gt=0)
    display_order: int = Field(default=1, ge=1)
    required: bool = True


class OutcomeMappingItem(BaseModel):
    learning_outcome_id: uuid.UUID
    competency_id: Optional[uuid.UUID] = None
    mapped_marks: Optional[float] = None


class AssessmentCreate(BaseModel):
    subject_id: uuid.UUID
    assessment_name: str = Field(..., min_length=3, max_length=255)
    assessment_type: AssessmentType = AssessmentType.INTERNAL_TEST
    academic_year: str = Field(..., min_length=4)
    semester: int = Field(..., ge=1, le=12)
    maximum_marks: float = Field(..., gt=0)
    passing_marks: Optional[float] = Field(None, ge=0)
    weightage_percentage: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    instructions: Optional[str] = None
    is_online_assessment: bool = True
    duration_minutes: Optional[int] = Field(60, ge=5, le=360)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    evaluation_mode: AssessmentEvaluationMode = AssessmentEvaluationMode.HYBRID
    attempt_limit: int = Field(default=1, ge=1, le=10)
    allow_review: bool = True
    questions: Optional[List[QuestionMappingItem]] = None
    outcome_mappings: Optional[List[OutcomeMappingItem]] = None


class AssessmentUpdate(BaseModel):
    assessment_name: Optional[str] = Field(None, min_length=3, max_length=255)
    assessment_type: Optional[AssessmentType] = None
    maximum_marks: Optional[float] = Field(None, gt=0)
    passing_marks: Optional[float] = Field(None, ge=0)
    weightage_percentage: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=360)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    attempt_limit: Optional[int] = Field(None, ge=1, le=10)
    allow_review: Optional[bool] = None
    questions: Optional[List[QuestionMappingItem]] = None
    outcome_mappings: Optional[List[OutcomeMappingItem]] = None


class AssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: uuid.UUID
    academic_year: str
    semester: int
    assessment_name: str
    assessment_type: str
    maximum_marks: float
    passing_marks: Optional[float] = None
    weightage_percentage: Optional[float] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    is_online_assessment: bool
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    evaluation_mode: str
    attempt_limit: int
    allow_review: bool
    status: str
    created_at: datetime
    updated_at: datetime
    question_count: int = 0
    total_configured_marks: float = 0.0


# ==========================================================
# Student Attempt & Response Schemas
# ==========================================================

class AttemptStartResponse(BaseModel):
    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_name: str
    duration_minutes: Optional[int]
    deadline_at: Optional[datetime]
    started_at: datetime
    attempt_number: int
    questions: List[StudentQuestionView]


class ResponseSaveRequest(BaseModel):
    question_id: uuid.UUID
    response_payload: Dict[str, Any]  # e.g. {"selected_option_ids": [...]} or {"text_answer": "..."}


class ResponseSaveBatchRequest(BaseModel):
    responses: List[ResponseSaveRequest]


class ResponseItemDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID
    response_payload: Optional[Dict[str, Any]] = None
    saved_at: datetime
    submitted_at: Optional[datetime] = None
    revision_count: int
    evaluation_status: str
    marks_awarded: Optional[float] = None
    feedback: Optional[str] = None
    is_auto_evaluated: bool


class AttemptDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_id: uuid.UUID
    assessment_id: uuid.UUID
    student_id: uuid.UUID
    attempt_number: int
    attempt_status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    total_marks: float
    marks_obtained: Optional[float] = None
    evaluation_status: str
    created_at: datetime
    responses: List[ResponseItemDetail] = []


# ==========================================================
# Evaluation & Grading Schemas
# ==========================================================

class ManualQuestionEvaluationRequest(BaseModel):
    question_id: uuid.UUID
    marks_awarded: float = Field(..., ge=0)
    feedback: Optional[str] = None


class BatchEvaluationRequest(BaseModel):
    evaluations: List[ManualQuestionEvaluationRequest]
    overall_remarks: Optional[str] = None


class ReleaseResultRequest(BaseModel):
    publish_to_official_records: bool = True
    verification_remarks: Optional[str] = "Evaluated and verified via Online Assessment Engine"


# ==========================================================
# Learning Engagement Telemetry Schemas
# ==========================================================

class EngagementEventCreate(BaseModel):
    assessment_id: uuid.UUID
    attempt_id: Optional[uuid.UUID] = None
    event_type: LearningEngagementEventType
    event_metadata: Optional[Dict[str, Any]] = None
    source: str = "WEB"


class EngagementEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    assessment_id: uuid.UUID
    attempt_id: Optional[uuid.UUID] = None
    event_type: str
    event_timestamp: datetime
    event_metadata: Optional[Dict[str, Any]] = None
    source: str


class LearningEngagementSummary(BaseModel):
    total_events: int
    participation_rate: float
    total_attempts: int
    completed_attempts: int
    in_progress_attempts: int
    average_revision_count: float
    total_answer_revisions: int
    limitations_disclaimer: str = (
        "This summary reflects observable platform interactions only (start, save, revise, submit). "
        "It does not directly measure internal cognitive attention, mental concentration, or conceptual understanding."
    )


# ==========================================================
# Assessment Analytics Schemas
# ==========================================================

class QuestionAnalyticsItem(BaseModel):
    question_id: uuid.UUID
    question_text: str
    question_type: str
    difficulty: str
    bloom_level: Optional[str] = None
    allocated_marks: float
    total_attempts: int
    correct_count: int
    incorrect_count: int
    partially_correct_count: int
    average_marks: float
    success_rate_percentage: float


class AssessmentAnalyticsResponse(BaseModel):
    assessment_id: uuid.UUID
    assessment_name: str
    maximum_marks: float
    total_enrolled_students: int
    total_attempts: int
    completed_submissions: int
    evaluated_submissions: int
    pending_evaluations: int
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None
    pass_rate_percentage: Optional[float] = None
    questions: List[QuestionAnalyticsItem] = []
    outcome_coverage: List[Dict[str, Any]] = []
