from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid

from app.models.enums import (
    RiskClassification,
    RiskModelType,
    RiskModelStatus,
    RiskTargetStatus,
    RiskJobType,
    RiskJobStatus,
    RiskPredictionStatus,
    RiskEvaluationType,
    EvidenceSufficiencyLevel,
)


# =========================================================================
# Target Schemas
# =========================================================================

class RiskTargetCreateRequest(BaseModel):
    subject_id: Optional[uuid.UUID] = None
    target_code: str = Field(..., max_length=50, examples=["COURSE_FAILURE_DEFICIT"])
    target_name: str = Field(..., max_length=255, examples=["Course Final Grade Deficit"])
    description: Optional[str] = None
    academic_period: str = Field(default="SEMESTER_FINAL", max_length=50)
    outcome_definition: str = Field(..., examples=["Final course aggregate marks below institutional minimum threshold"])
    positive_label_definition: str = Field(..., examples=["Final marks < 50.0%"])
    negative_label_definition: str = Field(..., examples=["Final marks >= 50.0%"])
    passing_threshold_percentage: float = Field(default=50.0, ge=0.0, le=100.0)
    prediction_horizon_weeks: int = Field(default=4, ge=1, le=52)
    is_institution_policy: bool = Field(default=True)


class RiskTargetUpdateRequest(BaseModel):
    target_name: Optional[str] = None
    description: Optional[str] = None
    passing_threshold_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    prediction_horizon_weeks: Optional[int] = Field(None, ge=1, le=52)
    status: Optional[RiskTargetStatus] = None
    is_institution_policy: Optional[bool] = None


class RiskTargetResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: Optional[uuid.UUID] = None
    target_code: str
    target_name: str
    description: Optional[str] = None
    academic_period: str
    outcome_definition: str
    positive_label_definition: str
    negative_label_definition: str
    passing_threshold_percentage: float
    prediction_horizon_weeks: int
    status: str
    is_institution_policy: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# Feature Snapshot & Dataset Schemas
# =========================================================================

class RiskFeatureSnapshotResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    target_id: Optional[uuid.UUID] = None
    observation_cutoff_date: datetime
    feature_vector_json: Dict[str, Any]
    feature_provenance_json: Dict[str, Any]
    evidence_sufficiency: str
    eligible_records_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetPreviewRequest(BaseModel):
    subject_id: uuid.UUID
    target_id: uuid.UUID
    cutoff_date: Optional[datetime] = None


class DatasetSampleItem(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    features: Dict[str, Any]
    target_label: Optional[int] = None
    has_sufficient_evidence: bool
    is_temporally_valid: bool


class DatasetPreviewResponse(BaseModel):
    subject_id: uuid.UUID
    target_id: uuid.UUID
    target_name: str
    total_candidates: int
    eligible_samples_count: int
    positive_class_count: int
    negative_class_count: int
    unlabeled_count: int
    readiness_status: str
    readiness_reasons: List[str]
    sample_preview: List[DatasetSampleItem]
    scientific_disclaimer: str


# =========================================================================
# Model Registry & Evaluation Schemas
# =========================================================================

class RiskModelTrainRequest(BaseModel):
    target_id: uuid.UUID
    model_type: RiskModelType = Field(default=RiskModelType.LOGISTIC_REGRESSION)
    version_tag: Optional[str] = None
    test_size: float = Field(default=0.25, ge=0.1, le=0.5)
    random_state: int = Field(default=42)
    force_train_if_imbalanced: bool = Field(default=False)


class RiskModelEvaluationResponse(BaseModel):
    id: uuid.UUID
    model_version_id: uuid.UUID
    evaluation_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    confusion_matrix_json: Dict[str, int] = Field(default_factory=dict)
    class_distribution_json: Dict[str, int] = Field(default_factory=dict)
    is_probability_calibrated: bool
    calibration_notes: Optional[str] = None
    comparison_to_baseline_json: Dict[str, Any] = Field(default_factory=dict)
    evaluation_report: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskModelVersionResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    target_id: uuid.UUID
    version_tag: str
    model_type: str
    feature_schema_version: str
    parameters_json: Dict[str, Any]
    training_sample_size: int
    positive_class_count: int
    negative_class_count: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    evaluations: List[RiskModelEvaluationResponse] = []

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# Prediction & Explanation Schemas
# =========================================================================

class RiskPredictionGenerateRequest(BaseModel):
    subject_id: uuid.UUID
    target_id: uuid.UUID
    target_student_id: Optional[uuid.UUID] = None
    cutoff_date: Optional[datetime] = None
    model_version_id: Optional[uuid.UUID] = None


class AcademicRiskExplanationItem(BaseModel):
    id: uuid.UUID
    feature_name: str
    feature_value: float
    contribution_weight: float
    explanation_text: str
    source_evidence_reference: Optional[str] = None
    is_adverse_factor: bool

    model_config = ConfigDict(from_attributes=True)


class AcademicRiskPredictionResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    target_id: uuid.UUID
    model_version_id: Optional[uuid.UUID] = None
    risk_classification: str
    risk_score: Optional[float] = None
    is_calibrated_probability: bool
    evidence_sufficiency: str
    prediction_cutoff_date: datetime
    prediction_status: str
    scientific_disclaimer: str
    created_at: datetime
    explanations: List[AcademicRiskExplanationItem] = []

    model_config = ConfigDict(from_attributes=True)


class StudentRiskProfileResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    subject_id: uuid.UUID
    subject_code: str
    subject_name: str
    target_id: uuid.UUID
    target_name: str
    risk_classification: str
    risk_score: Optional[float] = None
    is_calibrated_probability: bool
    evidence_sufficiency: str
    model_type: Optional[str] = None
    model_version_tag: Optional[str] = None
    prediction_cutoff_date: datetime
    explanations: List[AcademicRiskExplanationItem]
    historical_predictions_count: int
    supporting_academic_evidence: Dict[str, Any]
    scientific_disclaimer: str


class CohortRiskSummaryItem(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    risk_classification: str
    risk_score: Optional[float] = None
    evidence_sufficiency: str
    top_adverse_factor: Optional[str] = None


class CohortRiskSummaryResponse(BaseModel):
    subject_id: uuid.UUID
    subject_code: str
    subject_name: str
    target_id: uuid.UUID
    target_name: str
    total_enrolled: int
    analyzed_students_count: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    insufficient_evidence_count: int
    model_not_ready_count: int
    active_model_version: Optional[str] = None
    active_model_type: Optional[str] = None
    latest_prediction_date: Optional[datetime] = None
    students: List[CohortRiskSummaryItem]
    scientific_disclaimer: str


# =========================================================================
# Job & Readiness Schemas
# =========================================================================

class RiskJobResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    target_id: Optional[uuid.UUID] = None
    job_type: str
    status: str
    records_processed: int
    error_details: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskReadinessResponse(BaseModel):
    institution_id: uuid.UUID
    subject_id: Optional[uuid.UUID] = None
    target_id: Optional[uuid.UUID] = None
    is_target_configured: bool
    target_status: str
    total_historical_records: int
    labeled_samples_count: int
    positive_class_count: int
    negative_class_count: int
    is_dataset_ready_for_training: bool
    active_deployed_model: Optional[str] = None
    readiness_notes: List[str]
    scientific_disclaimer: str
