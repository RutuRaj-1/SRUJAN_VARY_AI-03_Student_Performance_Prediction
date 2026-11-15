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
    CompetencyEvidenceState,
    CompetencyEvidenceType,
    CareerAlignmentStatus,
    CareerSkillGapType,
    CareerGapSeverity,
    CareerRecommendationType,
    CareerRecommendationStatus,
    ProjectVerificationStatus,
    RoleRequirementImportance,
    RoleMappingStatus,
)

DEFAULT_CAREER_READINESS_DISCLAIMER = (
    "Career readiness evaluations reflect observed alignment between demonstrated academic, "
    "assessment, and verified practical project evidence against curated industry role competency profiles. "
    "This evaluation describes current evidence availability and development recommendations, "
    "and does NOT constitute a guarantee of employment, hiring prediction, or singular employability score."
)


class StudentProjectEvidence(Base):
    """
    Student-submitted practical project evidence (GitHub, portfolio, capstone, micro-lab)
    requiring faculty or mentor verification before becoming eligible career evidence.
    """
    __tablename__ = "student_project_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    technology_stack = Column(JSON, nullable=False, default=list)  # e.g. ["Python", "FastAPI", "React", "PostgreSQL"]
    repository_url = Column(String(512), nullable=True)
    portfolio_url = Column(String(512), nullable=True)
    documentation_url = Column(String(512), nullable=True)
    demonstrated_competencies = Column(JSON, nullable=False, default=list)  # e.g. ["RESTful API Architecture", "Database Design"]

    verification_status = Column(String(50), nullable=False, default=ProjectVerificationStatus.PENDING_REVIEW.value, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    reviewer = relationship("Profile")


class StudentCompetencyEvidence(Base):
    """
    Unified, explainable evidence ledger for student competencies.
    Aggregates verified theoretical assessments, topic mastery, practical projects, and faculty verifications.
    """
    __tablename__ = "student_competency_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_id = Column(UUID(as_uuid=True), ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True, index=True)
    
    competency_name = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False, default="PROGRAMMING", index=True)
    evidence_type = Column(String(50), nullable=False, default=CompetencyEvidenceType.THEORETICAL_ASSESSMENT.value, index=True)
    source_entity_type = Column(String(50), nullable=False)  # ASSESSMENT_RESPONSE, TOPIC_MASTERY_RESULT, STUDENT_PROJECT_EVIDENCE, CURRICULUM_SYLLABUS
    source_entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    evidence_state = Column(String(50), nullable=False, default=CompetencyEvidenceState.NOT_ASSESSED.value, index=True)
    score_or_metric = Column(Float, nullable=True)  # Percentage score (0-100) or rubric score
    evidence_summary = Column(Text, nullable=False)
    provenance_details = Column(JSON, nullable=True, default=dict)

    verified_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_eligible = Column(Boolean, nullable=False, default=True, index=True)
    exclusion_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    competency = relationship("Competency")
    verifier = relationship("Profile")


class CareerReadinessAnalysis(Base):
    """
    Deterministic, role-specific career readiness evaluation.
    Compares approved industry role requirements against verified student competency evidence.
    Does NOT output a singular composite percentage score to avoid misleading aggregation.
    """
    __tablename__ = "career_readiness_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("industry_role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    alignment_status = Column(String(50), nullable=False, default=CareerAlignmentStatus.INSUFFICIENT_EVIDENCE.value, index=True)
    total_requirements_count = Column(Integer, nullable=False, default=0)
    demonstrated_count = Column(Integer, nullable=False, default=0)
    developing_count = Column(Integer, nullable=False, default=0)
    insufficient_evidence_count = Column(Integer, nullable=False, default=0)
    not_assessed_count = Column(Integer, nullable=False, default=0)
    review_required_count = Column(Integer, nullable=False, default=0)

    core_competency_coverage = Column(Float, nullable=False, default=0.0)  # Percentage (0-100)
    practical_evidence_coverage = Column(Float, nullable=False, default=0.0)  # Percentage (0-100)
    faculty_reviewed_count = Column(Integer, nullable=False, default=0)

    summary_rationale = Column(Text, nullable=False)
    disclaimer = Column(Text, nullable=False, default=DEFAULT_CAREER_READINESS_DISCLAIMER)
    analysis_version = Column(String(50), nullable=False, default="v1.0-deterministic")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    role = relationship("IndustryRoleProfile")
    gap_findings = relationship("CareerSkillGapFinding", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("CareerDevelopmentRecommendation", back_populates="analysis", cascade="all, delete-orphan")


class CareerSkillGapFinding(Base):
    """
    Categorized industry skill gap discovery.
    Distinguishes Demonstrated Gap, Evidence Gap, Curriculum Gap, Practical Evidence Gap, and Mapping Gap.
    """
    __tablename__ = "career_skill_gap_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("career_readiness_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("industry_role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("industry_competency_requirements.id", ondelete="SET NULL"), nullable=True)

    competency_name = Column(String(255), nullable=False)
    importance = Column(String(50), nullable=False, default=RoleRequirementImportance.CORE.value)
    gap_type = Column(String(50), nullable=False, default=CareerSkillGapType.DEMONSTRATED_GAP.value, index=True)
    current_evidence_state = Column(String(50), nullable=False, default=CompetencyEvidenceState.NOT_ASSESSED.value)
    gap_severity = Column(String(50), nullable=False, default=CareerGapSeverity.MODERATE.value, index=True)

    rationale = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    evidence_needed = Column(Text, nullable=False)

    related_subject_id = Column(UUID(as_uuid=True), ForeignKey("academic_subjects.id", ondelete="SET NULL"), nullable=True)
    related_learning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("learning_outcomes.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(50), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    analysis = relationship("CareerReadinessAnalysis", back_populates="gap_findings")
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    role = relationship("IndustryRoleProfile")
    requirement = relationship("IndustryCompetencyRequirement")
    related_subject = relationship("AcademicSubject")
    related_learning_outcome = relationship("LearningOutcome")


class CareerDevelopmentRecommendation(Base):
    """
    Actionable career development roadmap items targeting identified skill gaps.
    Preserves distinct lifecycle from academic interventions while allowing optional linking.
    """
    __tablename__ = "career_development_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("career_readiness_analyses.id", ondelete="SET NULL"), nullable=True, index=True)
    gap_id = Column(UUID(as_uuid=True), ForeignKey("career_skill_gap_findings.id", ondelete="SET NULL"), nullable=True, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_academic_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("industry_role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    target_competency = Column(String(255), nullable=False)
    recommendation_type = Column(String(50), nullable=False, default=CareerRecommendationType.PRACTICAL_PROJECT.value, index=True)
    priority = Column(String(50), nullable=False, default=CareerGapSeverity.HIGH.value, index=True)
    status = Column(String(50), nullable=False, default=CareerRecommendationStatus.PROPOSED.value, index=True)

    action_plan = Column(Text, nullable=False)
    expected_evidence = Column(Text, nullable=False)
    estimated_duration_days = Column(Integer, nullable=False, default=14)

    # Optional bridge to Phase 08 academic intervention if an academic course gap exists
    academic_intervention_plan_id = Column(UUID(as_uuid=True), ForeignKey("academic_intervention_plans.id", ondelete="SET NULL"), nullable=True)

    student_notes = Column(Text, nullable=True)
    reviewer_feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
    student = relationship("StudentAcademicProfile")
    role = relationship("IndustryRoleProfile")
    analysis = relationship("CareerReadinessAnalysis", back_populates="recommendations")
    gap = relationship("CareerSkillGapFinding")
    academic_intervention_plan = relationship("AcademicInterventionPlan")
