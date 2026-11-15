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
    InterventionType,
    InterventionPriority,
    InterventionPlanStatus,
    InterventionActionStatus,
    InterventionRecommendationStatus,
    InterventionEventType,
    EvidenceSufficiencyLevel,
)

DEFAULT_INTERVENTION_DISCLAIMER = (
    "SCIENTIFIC GOVERNANCE NOTICE: Academic interventions are supportive, human-in-the-loop pedagogical "
    "recommendations designed to assist student learning and mastery development. Recommendations do NOT "
    "constitute disciplinary actions, clinical diagnoses, or fixed categorizations of student ability. "
    "All support plans require authorized faculty review and student-centered pacing."
)


class InterventionTemplate(Base):
    """
    Catalog of approved institutional intervention templates.
    """
    __tablename__ = "intervention_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    template_code = Column(String(64), nullable=False)
    template_name = Column(String(255), nullable=False)
    intervention_type = Column(String(50), nullable=False, default=InterventionType.TARGETED_REVISION.value)
    description = Column(Text, nullable=True)
    target_level = Column(String(30), nullable=False, default="TOPIC")  # TOPIC, UNIT, CLO, SUBJECT
    suggested_duration_hours = Column(Float, nullable=False, default=2.0)
    suggested_completion_days = Column(Integer, nullable=False, default=7)
    recommended_actions_template = Column(JSONB, nullable=False, default=list)
    required_resources = Column(JSONB, nullable=False, default=list)
    expected_evidence_type = Column(String(100), nullable=True)
    requires_faculty_review = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by_profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("Institution")
    subject = relationship("AcademicSubject")
    created_by = relationship("Profile", foreign_keys=[created_by_profile_id])

    __table_args__ = (
        UniqueConstraint("institution_id", "template_code", name="uq_intervention_template_inst_code"),
    )


class AcademicInterventionRecommendation(Base):
    """
    Evidence-grounded candidate recommendations produced by the recommendation engine.
    """
    __tablename__ = "academic_intervention_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True, index=True)
    risk_prediction_id = Column(UUID(as_uuid=True), ForeignKey("academic_risk_predictions.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_gap_id = Column(UUID(as_uuid=True), ForeignKey("learning_gap_findings.id", ondelete="SET NULL"), nullable=True, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("intervention_templates.id", ondelete="SET NULL"), nullable=True)

    recommendation_type = Column(String(50), nullable=False, default=InterventionType.TARGETED_REVISION.value)
    priority = Column(String(20), nullable=False, default=InterventionPriority.MEDIUM.value)
    rationale = Column(Text, nullable=False)
    source_evidence_summary = Column(JSONB, nullable=False, default=dict)
    evidence_sufficiency = Column(String(30), nullable=False, default=EvidenceSufficiencyLevel.MODERATE.value)
    proposed_action_title = Column(String(255), nullable=False)
    proposed_action_description = Column(Text, nullable=False)
    suggested_duration_days = Column(Integer, nullable=False, default=7)
    status = Column(String(30), nullable=False, default=InterventionRecommendationStatus.ACTIVE.value)
    scientific_disclaimer = Column(Text, nullable=False, default=DEFAULT_INTERVENTION_DISCLAIMER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
    risk_prediction = relationship("AcademicRiskPrediction")
    learning_gap = relationship("LearningGapFinding")
    template = relationship("InterventionTemplate")


class AcademicInterventionPlan(Base):
    """
    Structured, faculty-reviewed academic support plan assigned to a student.
    """
    __tablename__ = "academic_intervention_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True, index=True)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_recommendations.id", ondelete="SET NULL"), nullable=True)

    plan_title = Column(String(255), nullable=False)
    learning_objective = Column(Text, nullable=False)
    plan_status = Column(String(30), nullable=False, default=InterventionPlanStatus.DRAFT.value, index=True)
    assigned_faculty_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_by_faculty_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    faculty_review_notes = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    expected_outcome_evidence = Column(Text, nullable=True)
    scientific_disclaimer = Column(Text, nullable=False, default=DEFAULT_INTERVENTION_DISCLAIMER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
    recommendation = relationship("AcademicInterventionRecommendation")
    assigned_faculty = relationship("Profile", foreign_keys=[assigned_faculty_id])
    reviewed_by_faculty = relationship("Profile", foreign_keys=[reviewed_by_faculty_id])

    actions = relationship("AcademicInterventionAction", back_populates="plan", cascade="all, delete-orphan", order_by="AcademicInterventionAction.action_order")
    progress_events = relationship("InterventionProgressEvent", back_populates="plan", cascade="all, delete-orphan", order_by="InterventionProgressEvent.created_at.desc()")
    outcome_observations = relationship("InterventionOutcomeObservation", back_populates="plan", cascade="all, delete-orphan")


class AcademicInterventionAction(Base):
    """
    Individual concrete action item within an academic intervention plan.
    """
    __tablename__ = "academic_intervention_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    action_order = Column(Integer, nullable=False, default=1)
    action_title = Column(String(255), nullable=False)
    action_type = Column(String(50), nullable=False, default=InterventionType.TARGETED_REVISION.value)
    instructions = Column(Text, nullable=False)
    resource_references = Column(JSONB, nullable=False, default=list)
    estimated_effort_hours = Column(Float, nullable=False, default=1.0)
    due_date = Column(DateTime(timezone=True), nullable=True)
    action_status = Column(String(30), nullable=False, default=InterventionActionStatus.PROPOSED.value, index=True)

    student_completion_notes = Column(Text, nullable=True)
    student_submission_url = Column(String(512), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    faculty_feedback = Column(Text, nullable=True)
    verified_by_faculty_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plan = relationship("AcademicInterventionPlan", back_populates="actions")
    verified_by_faculty = relationship("Profile", foreign_keys=[verified_by_faculty_id])


class InterventionProgressEvent(Base):
    """
    Append-only audit ledger of lifecycle and progress events for an intervention plan.
    """
    __tablename__ = "intervention_progress_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    action_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_actions.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type = Column(String(50), nullable=False, default=InterventionEventType.PLAN_CREATED.value)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    event_notes = Column(Text, nullable=True)
    event_metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plan = relationship("AcademicInterventionPlan", back_populates="progress_events")
    action = relationship("AcademicInterventionAction")
    actor_profile = relationship("Profile")


class InterventionOutcomeObservation(Base):
    """
    Post-intervention evidence observation linking subsequent assessment or mastery results.
    """
    __tablename__ = "intervention_outcome_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True)

    baseline_mastery_percentage = Column(Float, nullable=True)
    followup_assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="SET NULL"), nullable=True)
    followup_score_obtained = Column(Float, nullable=True)
    followup_maximum_marks = Column(Float, nullable=True)
    followup_mastery_percentage = Column(Float, nullable=True)
    observation_notes = Column(Text, nullable=True)
    scientific_disclaimer = Column(Text, nullable=False, default=DEFAULT_INTERVENTION_DISCLAIMER)
    observed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plan = relationship("AcademicInterventionPlan", back_populates="outcome_observations")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
    followup_assessment = relationship("AcademicAssessment")
