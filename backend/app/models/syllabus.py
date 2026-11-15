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
    Text,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.enums import (
    DocumentStatus,
    BloomTaxonomyLevel,
    CompetencyCategory,
    IndustryMappingStatus,
    IndustryImportance,
    ReviewStatus,
)


class AcademicProgram(Base):
    __tablename__ = "academic_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    degree_type = Column(String(100), nullable=False, default="Bachelor of Technology")
    duration_years = Column(Integer, nullable=False, default=4)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution", backref="programs")
    subjects = relationship("AcademicSubject", back_populates="program", cascade="all, delete-orphan")


class AcademicSubject(Base):
    __tablename__ = "academic_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("academic_programs.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    academic_year = Column(String(50), nullable=False, default="2024-2025")
    regulation_version = Column(String(50), nullable=False, default="R22")
    credits = Column(Integer, nullable=False, default=4)
    total_hours = Column(Integer, nullable=False, default=45)
    description = Column(Text, nullable=True)
    prerequisites = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    program = relationship("AcademicProgram", back_populates="subjects")
    documents = relationship("SyllabusDocument", back_populates="subject", cascade="all, delete-orphan")
    units = relationship("SyllabusUnit", back_populates="subject", cascade="all, delete-orphan", order_by="SyllabusUnit.unit_number")
    learning_outcomes = relationship("LearningOutcome", back_populates="subject", cascade="all, delete-orphan")
    competency_mappings = relationship("SubjectCompetencyMapping", back_populates="subject", cascade="all, delete-orphan")
    gap_analyses = relationship("CurriculumGapAnalysis", back_populates="subject", cascade="all, delete-orphan")


class SyllabusDocument(Base):
    __tablename__ = "syllabus_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_path = Column(String(512), nullable=False)
    status = Column(String(50), nullable=False, default=DocumentStatus.UPLOADED.value, index=True)
    raw_text = Column(Text, nullable=True)
    extraction_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    subject = relationship("AcademicSubject", back_populates="documents")
    uploader = relationship("Profile")
    units = relationship("SyllabusUnit", back_populates="document", cascade="all, delete-orphan", order_by="SyllabusUnit.unit_number")
    reviews = relationship("SyllabusReviewHistory", back_populates="document", cascade="all, delete-orphan")


class SyllabusUnit(Base):
    __tablename__ = "syllabus_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    estimated_hours = Column(Integer, nullable=False, default=9)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("SyllabusDocument", back_populates="units")
    subject = relationship("AcademicSubject", back_populates="units")
    topics = relationship("SyllabusTopic", back_populates="unit", cascade="all, delete-orphan", order_by="SyllabusTopic.order_index")
    learning_outcomes = relationship("LearningOutcome", back_populates="unit")


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_units.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_name = Column(String(255), nullable=False)
    subtopics = Column(JSON, nullable=True, default=list)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    unit = relationship("SyllabusUnit", back_populates="topics")
    competency_mappings = relationship("SubjectCompetencyMapping", back_populates="topic")


class LearningOutcome(Base):
    __tablename__ = "learning_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_units.id", ondelete="SET NULL"), nullable=True, index=True)
    outcome_code = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    bloom_level = Column(String(50), nullable=False, default=BloomTaxonomyLevel.APPLY.value)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    subject = relationship("AcademicSubject", back_populates="learning_outcomes")
    unit = relationship("SyllabusUnit", back_populates="learning_outcomes")


class Competency(Base):
    __tablename__ = "competencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default=CompetencyCategory.THEORETICAL.value, index=True)
    bloom_level = Column(String(50), nullable=False, default=BloomTaxonomyLevel.UNDERSTAND.value)
    depth_level = Column(Integer, nullable=False, default=3)
    syllabus_evidence = Column(Text, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    mappings = relationship("SubjectCompetencyMapping", back_populates="competency", cascade="all, delete-orphan")


class SubjectCompetencyMapping(Base):
    __tablename__ = "subject_competency_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_units.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True)
    outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True)
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    subject = relationship("AcademicSubject", back_populates="competency_mappings")
    unit = relationship("SyllabusUnit")
    topic = relationship("SyllabusTopic", back_populates="competency_mappings")
    outcome = relationship("LearningOutcome")
    competency = relationship("Competency", back_populates="mappings")


class IndustryRoleProfile(Base):
    __tablename__ = "industry_role_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=True, index=True)
    role_title = Column(String(255), nullable=False, index=True)
    role_family = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    experience_tier = Column(String(50), nullable=False, default="Entry-Level / Fresher")
    version = Column(String(50), nullable=False, default="1.0")
    is_active = Column(Boolean, nullable=False, default=True)
    review_status = Column(String(50), nullable=False, default="APPROVED")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    requirements = relationship("IndustryCompetencyRequirement", back_populates="role", cascade="all, delete-orphan")
    gap_analyses = relationship("CurriculumGapAnalysis", back_populates="role", cascade="all, delete-orphan")


class IndustryCompetencyRequirement(Base):
    __tablename__ = "industry_competency_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("industry_role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True, index=True)
    competency_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default=CompetencyCategory.PROGRAMMING.value)
    required_depth = Column(Integer, nullable=False, default=3)
    importance = Column(String(50), nullable=False, default=IndustryImportance.HIGH.value)
    mapping_status = Column(String(50), nullable=False, default="APPROVED")
    source_reference = Column(String(255), nullable=True)
    rationale = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    role = relationship("IndustryRoleProfile", back_populates="requirements")
    academic_competency = relationship("Competency")
    gap_analyses = relationship("CurriculumGapAnalysis", back_populates="industry_competency", cascade="all, delete-orphan")


class CurriculumGapAnalysis(Base):
    __tablename__ = "curriculum_gap_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("industry_role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    industry_competency_id = Column(UUID(as_uuid=True), ForeignKey("industry_competency_requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default=IndustryMappingStatus.MISSING.value)
    rationale = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    subject = relationship("AcademicSubject", back_populates="gap_analyses")
    role = relationship("IndustryRoleProfile", back_populates="gap_analyses")
    industry_competency = relationship("IndustryCompetencyRequirement", back_populates="gap_analyses")
    academic_competency = relationship("Competency")


class SyllabusReviewHistory(Base):
    __tablename__ = "syllabus_review_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("syllabus_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    document = relationship("SyllabusDocument", back_populates="reviews")
    reviewer = relationship("Profile")
