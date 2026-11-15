import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MasteryAnalysisJob(Base):
    __tablename__ = "mastery_analysis_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    curriculum_version = Column(String(50), nullable=True)
    calculation_version = Column(String(50), nullable=False, default="v1.0-deterministic")

    status = Column(String(50), nullable=False, default="PENDING", index=True)
    total_evidence_examined = Column(Integer, nullable=False, default=0)
    eligible_evidence_count = Column(Integer, nullable=False, default=0)
    excluded_evidence_count = Column(Integer, nullable=False, default=0)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_summary = Column(Text, nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    creator = relationship("Profile")
    evidence_records = relationship("MasteryEvidenceRecord", back_populates="job", cascade="all, delete-orphan")
    topic_results = relationship("TopicMasteryResult", back_populates="job", cascade="all, delete-orphan")
    outcome_results = relationship("LearningOutcomeAttainmentResult", back_populates="job", cascade="all, delete-orphan")
    learning_gaps = relationship("LearningGapFinding", back_populates="job", cascade="all, delete-orphan")


class MasteryEvidenceRecord(Base):
    __tablename__ = "mastery_evidence_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_job_id = Column(UUID(as_uuid=True), ForeignKey("mastery_analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True, index=True)

    source_entity_type = Column(String(50), nullable=False)  # ASSESSMENT_RESPONSE, OFFICIAL_GRADEBOOK_RECORD
    source_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="SET NULL"), nullable=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=True)

    marks_obtained = Column(Float, nullable=False, default=0.0)
    maximum_marks = Column(Float, nullable=False, default=1.0)
    eligibility_status = Column(String(50), nullable=False, default="ELIGIBLE", index=True)  # ELIGIBLE, EXCLUDED
    exclusion_reason = Column(String(100), nullable=True)
    mapping_status = Column(String(50), nullable=False, default="APPROVED_MAPPING")
    evaluation_status = Column(String(50), nullable=False, default="EVALUATED")
    verification_status = Column(String(50), nullable=True)
    bloom_level = Column(String(50), nullable=True)
    is_practice_assessment = Column(Boolean, nullable=False, default=False)

    evidence_timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    job = relationship("MasteryAnalysisJob", back_populates="evidence_records")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
    assessment = relationship("AcademicAssessment")
    question = relationship("AssessmentQuestion")
    attempt = relationship("AssessmentAttempt")


class TopicMasteryResult(Base):
    __tablename__ = "topic_mastery_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_job_id = Column(UUID(as_uuid=True), ForeignKey("mastery_analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    curriculum_version = Column(String(50), nullable=True)

    eligible_question_count = Column(Integer, nullable=False, default=0)
    eligible_attempt_count = Column(Integer, nullable=False, default=0)
    marks_obtained = Column(Float, nullable=False, default=0.0)
    maximum_marks = Column(Float, nullable=False, default=0.0)
    mastery_percentage = Column(Float, nullable=True)  # NULL if insufficient evidence

    evidence_sufficiency = Column(String(50), nullable=False, default="INSUFFICIENT", index=True)
    confidence_category = Column(String(50), nullable=False, default="LOW")
    mastery_status = Column(String(50), nullable=False, default="INSUFFICIENT_EVIDENCE", index=True)

    evidence_window_start = Column(DateTime(timezone=True), nullable=True)
    evidence_window_end = Column(DateTime(timezone=True), nullable=True)
    calculation_version = Column(String(50), nullable=False, default="v1.0-deterministic")
    calculated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("analysis_job_id", "student_id", "topic_id", name="uq_job_student_topic"),
    )

    # Relationships
    job = relationship("MasteryAnalysisJob", back_populates="topic_results")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")


class LearningOutcomeAttainmentResult(Base):
    __tablename__ = "learning_outcome_attainment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_job_id = Column(UUID(as_uuid=True), ForeignKey("mastery_analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="CASCADE"), nullable=False, index=True)

    eligible_question_count = Column(Integer, nullable=False, default=0)
    mapped_marks = Column(Float, nullable=False, default=0.0)
    marks_obtained = Column(Float, nullable=False, default=0.0)
    attainment_percentage = Column(Float, nullable=True)  # NULL if insufficient evidence

    evidence_sufficiency = Column(String(50), nullable=False, default="INSUFFICIENT", index=True)
    confidence_category = Column(String(50), nullable=False, default="LOW")
    attainment_status = Column(String(50), nullable=False, default="INSUFFICIENT_EVIDENCE", index=True)

    calculation_version = Column(String(50), nullable=False, default="v1.0-deterministic")
    calculated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("analysis_job_id", "student_id", "learning_outcome_id", name="uq_job_student_outcome"),
    )

    # Relationships
    job = relationship("MasteryAnalysisJob", back_populates="outcome_results")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    learning_outcome = relationship("LearningOutcome")


class LearningGapFinding(Base):
    __tablename__ = "learning_gap_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_job_id = Column(UUID(as_uuid=True), ForeignKey("mastery_analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True, index=True)

    finding_type = Column(String(80), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default="MEDIUM", index=True)
    evidence_summary = Column(Text, nullable=False)
    supporting_evidence_refs = Column(JSON, nullable=True, default=dict)
    recommended_review_action = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="OPEN", index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("MasteryAnalysisJob", back_populates="learning_gaps")
    student = relationship("StudentAcademicProfile")
    subject = relationship("AcademicSubject")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
