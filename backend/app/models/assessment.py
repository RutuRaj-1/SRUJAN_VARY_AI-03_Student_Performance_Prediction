import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Float,
    Text,
    ForeignKey,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.enums import (
    QuestionType,
    QuestionDifficulty,
    QuestionEvaluationMethod,
    AttemptStatus,
    ResponseEvaluationStatus,
    LearningEngagementEventType,
    AssessmentOnlineStatus,
    AssessmentEvaluationMode,
)


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_units.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True, index=True)
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True, index=True)

    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default=QuestionType.MCQ.value)
    difficulty = Column(String(50), nullable=False, default=QuestionDifficulty.MEDIUM.value)
    bloom_level = Column(String(50), nullable=True)
    default_marks = Column(Float, nullable=False, default=1.0)
    explanation = Column(Text, nullable=True)
    expected_answer = Column(Text, nullable=True)
    evaluation_method = Column(String(50), nullable=False, default=QuestionEvaluationMethod.AUTOMATIC.value)
    code_language = Column(String(50), nullable=True)
    code_template = Column(Text, nullable=True)
    code_test_cases = Column(JSON, nullable=True, default=list)
    created_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    verification_status = Column(String(50), nullable=False, default="APPROVED")
    version = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    subject = relationship("AcademicSubject")
    unit = relationship("SyllabusUnit")
    topic = relationship("SyllabusTopic")
    learning_outcome = relationship("LearningOutcome")
    competency = relationship("Competency")
    creator = relationship("Profile")
    options = relationship("AssessmentQuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="AssessmentQuestionOption.display_order")
    mappings = relationship("AssessmentQuestionMapping", back_populates="question", cascade="all, delete-orphan")


class AssessmentQuestionOption(Base):
    __tablename__ = "assessment_question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_text = Column(Text, nullable=False)
    display_order = Column(Integer, nullable=False, default=1)
    is_correct = Column(Boolean, nullable=False, default=False)
    explanation = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    question = relationship("AssessmentQuestion", back_populates="options")


class AssessmentQuestionMapping(Base):
    __tablename__ = "assessment_question_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    marks_allocated = Column(Float, nullable=False, default=1.0)
    display_order = Column(Integer, nullable=False, default=1)
    required = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question_map"),
    )

    # Relationships
    assessment = relationship("AcademicAssessment", back_populates="question_mappings")
    question = relationship("AssessmentQuestion", back_populates="mappings")


class AssessmentLearningOutcomeMapping(Base):
    __tablename__ = "assessment_learning_outcome_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True, index=True)

    mapped_marks = Column(Float, nullable=True)
    mapping_type = Column(String(50), nullable=False, default="PRIMARY")
    mapping_status = Column(String(50), nullable=False, default="APPROVED")
    created_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("assessment_id", "learning_outcome_id", name="uq_assessment_outcome_map"),
    )

    # Relationships
    assessment = relationship("AcademicAssessment", back_populates="outcome_mappings")
    learning_outcome = relationship("LearningOutcome")
    competency = relationship("Competency")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    attempt_number = Column(Integer, nullable=False, default=1)
    attempt_status = Column(String(50), nullable=False, default=AttemptStatus.IN_PROGRESS.value, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    deadline_at = Column(DateTime(timezone=True), nullable=True)
    total_marks = Column(Float, nullable=False, default=0.0)
    marks_obtained = Column(Float, nullable=True)
    evaluation_status = Column(String(50), nullable=False, default="NOT_EVALUATED")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("assessment_id", "student_id", "attempt_number", name="uq_assessment_student_attempt"),
    )

    # Relationships
    assessment = relationship("AcademicAssessment", back_populates="attempts")
    student = relationship("StudentAcademicProfile")
    responses = relationship("AssessmentResponse", back_populates="attempt", cascade="all, delete-orphan")
    engagement_events = relationship("LearningEngagementEvent", back_populates="attempt", cascade="all, delete-orphan")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False, index=True)

    response_payload = Column(JSON, nullable=True, default=dict)
    saved_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    revision_count = Column(Integer, nullable=False, default=0)
    evaluation_status = Column(String(50), nullable=False, default=ResponseEvaluationStatus.PENDING.value)
    marks_awarded = Column(Float, nullable=True)
    is_auto_evaluated = Column(Boolean, nullable=False, default=False)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    feedback = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_response"),
    )

    # Relationships
    attempt = relationship("AssessmentAttempt", back_populates="responses")
    question = relationship("AssessmentQuestion")
    evaluator = relationship("Profile")
    rubric_evaluations = relationship("AssessmentRubricEvaluation", back_populates="response", cascade="all, delete-orphan")


class AssessmentRubric(Base):
    __tablename__ = "assessment_rubrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_rubric_marks = Column(Float, nullable=False, default=10.0)
    created_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    assessment = relationship("AcademicAssessment", back_populates="rubrics")
    criteria = relationship("AssessmentRubricCriteria", back_populates="rubric", cascade="all, delete-orphan", order_by="AssessmentRubricCriteria.display_order")


class AssessmentRubricCriteria(Base):
    __tablename__ = "assessment_rubric_criteria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rubric_id = Column(UUID(as_uuid=True), ForeignKey("assessment_rubrics.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    max_criterion_marks = Column(Float, nullable=False, default=5.0)
    levels_json = Column(JSON, nullable=False, default=list)
    display_order = Column(Integer, nullable=False, default=1)

    # Relationships
    rubric = relationship("AssessmentRubric", back_populates="criteria")


class AssessmentRubricEvaluation(Base):
    __tablename__ = "assessment_rubric_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("assessment_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(UUID(as_uuid=True), ForeignKey("assessment_rubric_criteria.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    awarded_marks = Column(Float, nullable=False, default=0.0)
    feedback = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    response = relationship("AssessmentResponse", back_populates="rubric_evaluations")
    criterion = relationship("AssessmentRubricCriteria")
    evaluator = relationship("Profile")


class LearningEngagementEvent(Base):
    __tablename__ = "learning_engagement_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("assessment_attempts.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type = Column(String(50), nullable=False, index=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    event_metadata = Column(JSON, nullable=True, default=dict)
    source = Column(String(50), nullable=False, default="WEB")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    student = relationship("StudentAcademicProfile")
    assessment = relationship("AcademicAssessment")
    attempt = relationship("AssessmentAttempt", back_populates="engagement_events")
