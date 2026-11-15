import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    BigInteger,
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
    AssessmentType,
    AssessmentResultStatus,
    AttendanceStatus,
    RecordVerificationStatus,
    DataQualitySeverity,
    ImportCategory,
    ImportJobStatus,
)


class StudentAcademicProfile(Base):
    __tablename__ = "student_academic_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("academic_programs.id", ondelete="RESTRICT"), nullable=False, index=True)

    enrollment_number = Column(String(100), nullable=False, index=True)
    admission_number = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    department = Column(String(100), nullable=False)
    admission_year = Column(Integer, nullable=False)
    current_semester = Column(Integer, nullable=False, default=1)
    academic_status = Column(String(50), nullable=False, default="ENROLLED")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Institutional uniqueness constraint
    __table_args__ = (
        UniqueConstraint("institution_id", "enrollment_number", name="uq_institution_student_enrollment"),
    )

    # Relationships
    institution = relationship("Institution")
    profile = relationship("Profile")
    program = relationship("AcademicProgram")
    enrollments = relationship("StudentSubjectEnrollment", back_populates="student", cascade="all, delete-orphan")
    assessment_records = relationship("StudentAssessmentRecord", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("StudentAttendanceRecord", back_populates="student", cascade="all, delete-orphan")


class StudentSubjectEnrollment(Base):
    __tablename__ = "student_subject_enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)

    academic_year = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    enrollment_status = Column(String(50), nullable=False, default="ACTIVE")
    enrolled_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "academic_year", "semester", name="uq_student_subject_term_enrollment"),
    )

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile", back_populates="enrollments")
    subject = relationship("AcademicSubject")


class AcademicAssessment(Base):
    __tablename__ = "academic_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)

    academic_year = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    assessment_name = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False, default=AssessmentType.INTERNAL_TEST.value)
    maximum_marks = Column(Float, nullable=False)
    passing_marks = Column(Float, nullable=True)
    weightage_percentage = Column(Float, nullable=True)
    assessment_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    is_online_assessment = Column(Boolean, nullable=False, default=False)
    duration_minutes = Column(Integer, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    evaluation_mode = Column(String(50), nullable=False, default="HYBRID")
    attempt_limit = Column(Integer, nullable=False, default=1)
    allow_review = Column(Boolean, nullable=False, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="SCHEDULED")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("subject_id", "academic_year", "semester", "assessment_name", name="uq_subject_term_assessment"),
    )

    # Relationships
    institution = relationship("Institution")
    subject = relationship("AcademicSubject")
    creator = relationship("Profile")
    records = relationship("StudentAssessmentRecord", back_populates="assessment", cascade="all, delete-orphan")
    question_mappings = relationship("AssessmentQuestionMapping", back_populates="assessment", cascade="all, delete-orphan", order_by="AssessmentQuestionMapping.display_order")
    outcome_mappings = relationship("AssessmentLearningOutcomeMapping", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")
    rubrics = relationship("AssessmentRubric", back_populates="assessment", cascade="all, delete-orphan")


class StudentAssessmentRecord(Base):
    __tablename__ = "student_assessment_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("academic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)

    marks_obtained = Column(Float, nullable=True)
    maximum_marks_snapshot = Column(Float, nullable=False)
    result_status = Column(String(50), nullable=False, default=AssessmentResultStatus.PENDING.value)
    source_type = Column(String(50), nullable=False, default="MANUAL")
    verification_status = Column(String(50), nullable=False, default=RecordVerificationStatus.IMPORTED.value)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    source_reference = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "assessment_id", name="uq_student_assessment_record"),
    )

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile", back_populates="assessment_records")
    assessment = relationship("AcademicAssessment", back_populates="records")
    recorder = relationship("Profile", foreign_keys=[recorded_by])
    verifier = relationship("Profile", foreign_keys=[verified_by])


class StudentAttendanceRecord(Base):
    __tablename__ = "student_attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)

    academic_year = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    attendance_date = Column(DateTime(timezone=True), nullable=False)
    session_name = Column(String(100), nullable=False, default="Regular Session")
    attendance_status = Column(String(50), nullable=False, default=AttendanceStatus.PRESENT.value)
    source_type = Column(String(50), nullable=False, default="MANUAL")
    verification_status = Column(String(50), nullable=False, default=RecordVerificationStatus.IMPORTED.value)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    source_reference = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "attendance_date", "session_name", name="uq_student_attendance_session"),
    )

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile", back_populates="attendance_records")
    subject = relationship("AcademicSubject")
    recorder = relationship("Profile", foreign_keys=[recorded_by])
    verifier = relationship("Profile", foreign_keys=[verified_by])


class AcademicImportJob(Base):
    __tablename__ = "academic_import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_path = Column(String(512), nullable=False)
    import_category = Column(String(50), nullable=False, default=ImportCategory.STUDENTS.value)
    status = Column(String(50), nullable=False, default=ImportJobStatus.PENDING.value)

    total_rows = Column(Integer, nullable=False, default=0)
    valid_rows = Column(Integer, nullable=False, default=0)
    invalid_rows = Column(Integer, nullable=False, default=0)
    duplicate_rows = Column(Integer, nullable=False, default=0)
    imported_rows = Column(Integer, nullable=False, default=0)

    preview_data = Column(JSON, nullable=True)
    error_summary = Column(JSON, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    uploader = relationship("Profile")
    errors = relationship("AcademicImportError", back_populates="job", cascade="all, delete-orphan")


class AcademicImportError(Base):
    __tablename__ = "academic_import_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("academic_import_jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    row_number = Column(Integer, nullable=False)
    column_name = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    error_code = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    job = relationship("AcademicImportJob", back_populates="errors")


class AcademicDataQualityFinding(Base):
    __tablename__ = "academic_data_quality_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_identifier = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default=DataQualitySeverity.WARNING.value)
    description = Column(Text, nullable=False)
    source_record = Column(JSON, nullable=True)
    recommended_action = Column(Text, nullable=True)
    resolution_status = Column(String(50), nullable=False, default="OPEN")
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    institution = relationship("Institution")
    resolver = relationship("Profile")


class AcademicRecordAudit(Base):
    __tablename__ = "academic_record_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    institution = relationship("Institution")
    actor = relationship("Profile")
