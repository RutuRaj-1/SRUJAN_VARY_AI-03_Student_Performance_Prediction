import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
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

DEFAULT_RISK_DISCLAIMER = (
    "SCIENTIFIC GOVERNANCE NOTICE: Academic risk predictions represent probabilistic or rule-based "
    "decision-support indicators derived from verified academic evidence up to the prediction cutoff. "
    "They do NOT constitute academic evaluations, definitive forecasts of student failure, diagnoses, "
    "or measures of student intelligence, and must NEVER be used to penalize students or make automated high-stakes decisions."
)


class AcademicRiskTarget(Base):
    """
    Institution-configured academic outcome targets defining what future difficulty means.
    """
    __tablename__ = "academic_risk_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=True, index=True)
    target_code = Column(String(50), nullable=False)
    target_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    academic_period = Column(String(50), nullable=False, default="SEMESTER_FINAL")
    outcome_definition = Column(Text, nullable=False)
    positive_label_definition = Column(Text, nullable=False)
    negative_label_definition = Column(Text, nullable=False)
    passing_threshold_percentage = Column(Float, nullable=False, default=50.0)
    prediction_horizon_weeks = Column(Integer, nullable=False, default=4)
    status = Column(String(30), nullable=False, default=RiskTargetStatus.NOT_CONFIGURED.value, index=True)
    is_institution_policy = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution")
    subject = relationship("AcademicSubject")

    __table_args__ = (
        UniqueConstraint("institution_id", "target_code", "subject_id", name="uq_institution_target_subject"),
    )


class RiskFeatureSnapshot(Base):
    """
    Immutable timestamped feature vector with strict observation cutoff for temporal leakage prevention.
    """
    __tablename__ = "risk_feature_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    observation_cutoff_date = Column(DateTime(timezone=True), nullable=False, index=True)
    feature_vector_json = Column(JSONB, nullable=False, default=dict)
    feature_provenance_json = Column(JSONB, nullable=False, default=dict)
    evidence_sufficiency = Column(String(30), nullable=False, default=EvidenceSufficiencyLevel.INSUFFICIENT.value)
    eligible_records_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    target = relationship("AcademicRiskTarget")


class RiskModelVersion(Base):
    """
    Model metadata, versioning, deployment state, and governance tracking.
    """
    __tablename__ = "risk_model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_targets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag = Column(String(50), nullable=False)
    model_type = Column(String(30), nullable=False, default=RiskModelType.DETERMINISTIC_RULES.value)
    feature_schema_version = Column(String(50), nullable=False, default="1.0")
    parameters_json = Column(JSONB, nullable=False, default=dict)
    artifact_path = Column(String(255), nullable=True)
    training_sample_size = Column(Integer, nullable=False, default=0)
    positive_class_count = Column(Integer, nullable=False, default=0)
    negative_class_count = Column(Integer, nullable=False, default=0)
    status = Column(String(30), nullable=False, default=RiskModelStatus.MODEL_NOT_READY.value, index=True)
    is_active = Column(Boolean, nullable=False, default=False)
    trained_by_profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution")
    target = relationship("AcademicRiskTarget")
    trained_by = relationship("Profile")
    evaluations = relationship("RiskModelEvaluation", back_populates="model_version", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("institution_id", "target_id", "version_tag", name="uq_institution_target_version"),
    )


class RiskModelEvaluation(Base):
    """
    Model performance metrics, validation strategy, and baseline comparisons.
    """
    __tablename__ = "risk_model_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("risk_model_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluation_type = Column(String(30), nullable=False, default=RiskEvaluationType.TEMPORAL_VALIDATION.value)
    accuracy = Column(Float, nullable=False, default=0.0)
    precision = Column(Float, nullable=False, default=0.0)
    recall = Column(Float, nullable=False, default=0.0)
    f1_score = Column(Float, nullable=False, default=0.0)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    confusion_matrix_json = Column(JSONB, nullable=False, default=dict)
    class_distribution_json = Column(JSONB, nullable=False, default=dict)
    is_probability_calibrated = Column(Boolean, nullable=False, default=False)
    calibration_notes = Column(Text, nullable=True)
    comparison_to_baseline_json = Column(JSONB, nullable=False, default=dict)
    evaluation_report = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    model_version = relationship("RiskModelVersion", back_populates="evaluations")


class AcademicRiskPrediction(Base):
    """
    Time-bounded risk prediction result with explainability links and provenance.
    """
    __tablename__ = "academic_risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_targets.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("risk_model_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("risk_feature_snapshots.id", ondelete="SET NULL"), nullable=True, index=True)

    risk_classification = Column(String(30), nullable=False, default=RiskClassification.MODEL_NOT_READY.value, index=True)
    risk_score = Column(Float, nullable=True)
    is_calibrated_probability = Column(Boolean, nullable=False, default=False)
    evidence_sufficiency = Column(String(30), nullable=False, default=EvidenceSufficiencyLevel.INSUFFICIENT.value)
    prediction_cutoff_date = Column(DateTime(timezone=True), nullable=False)
    prediction_status = Column(String(30), nullable=False, default=RiskPredictionStatus.ACTIVE.value, index=True)
    scientific_disclaimer = Column(Text, nullable=False, default=DEFAULT_RISK_DISCLAIMER)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    target = relationship("AcademicRiskTarget")
    model_version = relationship("RiskModelVersion")
    snapshot = relationship("RiskFeatureSnapshot")
    explanations = relationship("AcademicRiskPredictionExplanation", back_populates="prediction", cascade="all, delete-orphan")


class AcademicRiskPredictionExplanation(Base):
    """
    Grounded feature contributions and evidence references explaining the prediction.
    """
    __tablename__ = "academic_risk_prediction_explanations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(100), nullable=False)
    feature_value = Column(Float, nullable=False)
    contribution_weight = Column(Float, nullable=False)
    explanation_text = Column(Text, nullable=False)
    source_evidence_reference = Column(String(255), nullable=True)
    is_adverse_factor = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    prediction = relationship("AcademicRiskPrediction", back_populates="explanations")


class RiskPredictionJob(Base):
    """
    Tracks asynchronous prediction generation, training jobs, and dataset validations.
    """
    __tablename__ = "risk_prediction_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    job_type = Column(String(30), nullable=False, default=RiskJobType.BATCH_PREDICTION.value)
    triggered_by_profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), nullable=False, default=RiskJobStatus.PENDING.value, index=True)
    records_processed = Column(Integer, nullable=False, default=0)
    parameters_json = Column(JSONB, nullable=False, default=dict)
    error_details = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution")
    target = relationship("AcademicRiskTarget")
    triggered_by = relationship("Profile")
