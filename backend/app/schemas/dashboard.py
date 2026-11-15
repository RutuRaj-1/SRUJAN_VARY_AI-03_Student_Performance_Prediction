"""
Unified Dashboard Pydantic Schemas for Phase 10: Unified Intelligence Dashboard.
Enforces role-specific responses, metadata provenance, data freshness timestamps,
and strict non-aggregation policies (no artificial composite scores).
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DataFreshnessInfo(BaseModel):
    last_updated_at: Optional[datetime] = None
    source_module: str
    freshness_status: str = Field(
        default="FRESH",
        description="Freshness state: FRESH, RECENT, STALE, or NOT_AVAILABLE"
    )
    is_snapshot: bool = False
    details: Optional[str] = None


class DashboardFilterParams(BaseModel):
    academic_year: Optional[str] = None
    semester: Optional[int] = None
    program_id: Optional[uuid.UUID] = None
    subject_id: Optional[uuid.UUID] = None
    student_id: Optional[uuid.UUID] = None


# =========================================================================
# 1. Student Dashboard Schemas
# =========================================================================

class StudentProfileHeader(BaseModel):
    id: uuid.UUID
    full_name: str
    enrollment_number: str
    program_name: str
    department: str
    current_semester: int
    institution_name: str
    academic_status: str


class StudentAcademicPerformanceCard(BaseModel):
    average_marks: Optional[float] = None
    attendance_rate: Optional[float] = None
    total_records: int = 0
    verified_records_count: int = 0
    pending_records_count: int = 0
    enrolled_subjects_count: int = 0
    freshness: DataFreshnessInfo


class StudentMasterySummaryCard(BaseModel):
    topics_assessed_count: int = 0
    topics_demonstrated_count: int = 0
    topics_developing_count: int = 0
    topics_insufficient_evidence_count: int = 0
    clo_attainment_pct: Optional[float] = None
    active_learning_gaps_count: int = 0
    freshness: DataFreshnessInfo


class StudentRiskSummaryCard(BaseModel):
    has_prediction: bool = False
    risk_classification: Optional[str] = None
    risk_probability: Optional[float] = None
    prediction_horizon: Optional[str] = None
    primary_adverse_factors: List[str] = Field(default_factory=list)
    protective_factors: List[str] = Field(default_factory=list)
    prediction_timestamp: Optional[datetime] = None
    model_version: Optional[str] = None
    disclaimer: str = (
        "Academic risk predictions indicate potential difficulty under observed conditions, "
        "not guaranteed academic failure. Predictions are intended to guide timely academic support."
    )
    freshness: DataFreshnessInfo


class StudentInterventionSummaryCard(BaseModel):
    active_plans_count: int = 0
    pending_actions_count: int = 0
    completed_actions_count: int = 0
    latest_plan_title: Optional[str] = None
    faculty_mentor_name: Optional[str] = None
    freshness: DataFreshnessInfo


class StudentCareerSummaryCard(BaseModel):
    analyzed_roles_count: int = 0
    target_role_title: Optional[str] = None
    core_coverage_pct: Optional[float] = None
    practical_coverage_pct: Optional[float] = None
    alignment_status: Optional[str] = None
    verified_projects_count: int = 0
    pending_projects_count: int = 0
    active_skill_gaps_count: int = 0
    freshness: DataFreshnessInfo


class StudentOverviewResponse(BaseModel):
    student_profile: StudentProfileHeader
    academic_performance: StudentAcademicPerformanceCard
    mastery_summary: StudentMasterySummaryCard
    risk_summary: StudentRiskSummaryCard
    intervention_summary: StudentInterventionSummaryCard
    career_summary: StudentCareerSummaryCard
    system_freshness: datetime = Field(default_factory=datetime.utcnow)


# =========================================================================
# 2. Faculty Dashboard Schemas
# =========================================================================

class FacultySubjectItem(BaseModel):
    subject_id: uuid.UUID
    code: str
    name: str
    semester: int
    enrolled_students_count: int = 0
    average_attendance: Optional[float] = None
    average_marks: Optional[float] = None


class FacultyVerificationQueue(BaseModel):
    pending_academic_records: int = 0
    pending_interventions_review: int = 0
    pending_practical_projects: int = 0


class FacultyCohortRiskOverview(BaseModel):
    high_risk_students_count: int = 0
    moderate_risk_students_count: int = 0
    low_risk_students_count: int = 0
    learning_gaps_flagged_count: int = 0
    active_interventions_count: int = 0


class FacultyOverviewResponse(BaseModel):
    faculty_name: str
    institution_name: str
    department: str
    assigned_subjects: List[FacultySubjectItem] = Field(default_factory=list)
    total_students_monitored: int = 0
    verification_queue: FacultyVerificationQueue
    cohort_risk_overview: FacultyCohortRiskOverview
    freshness: DataFreshnessInfo


# =========================================================================
# 3. Institution Admin Dashboard Schemas
# =========================================================================

class InstitutionSummaryCounts(BaseModel):
    total_active_students: int = 0
    total_faculty: int = 0
    total_programs: int = 0
    total_subjects: int = 0


class InstitutionAcademicDataStatus(BaseModel):
    total_academic_records: int = 0
    verified_records_pct: float = 0.0
    data_quality_findings_count: int = 0


class InstitutionMasteryOverview(BaseModel):
    mastery_demonstrated_pct: float = 0.0
    mastery_developing_pct: float = 0.0
    insufficient_evidence_pct: float = 0.0
    total_evaluated_topics: int = 0


class InstitutionRiskDistribution(BaseModel):
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    unscreened_count: int = 0


class InstitutionInterventionMetrics(BaseModel):
    active_plans_count: int = 0
    completed_plans_count: int = 0
    pending_review_count: int = 0


class InstitutionCareerReadinessOverview(BaseModel):
    students_evaluated_count: int = 0
    ready_students_count: int = 0
    approaching_students_count: int = 0
    developing_students_count: int = 0
    verified_projects_total: int = 0


class InstitutionOverviewResponse(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
    institution_code: str
    summary_counts: InstitutionSummaryCounts
    academic_data_status: InstitutionAcademicDataStatus
    mastery_overview: InstitutionMasteryOverview
    risk_distribution: InstitutionRiskDistribution
    intervention_metrics: InstitutionInterventionMetrics
    career_readiness_overview: InstitutionCareerReadinessOverview
    freshness: DataFreshnessInfo


# =========================================================================
# 4. Placement Officer Dashboard Schemas (Firewalled from Risk & Interventions)
# =========================================================================

class PlacementReadinessDistribution(BaseModel):
    ready_count: int = 0
    approaching_count: int = 0
    developing_count: int = 0
    emerging_or_unassessed_count: int = 0


class PlacementProjectVerificationSummary(BaseModel):
    verified_projects_count: int = 0
    pending_verification_count: int = 0


class SkillGapItem(BaseModel):
    competency_name: str
    gap_type: str
    affected_students_count: int = 0


class PlacementOverviewResponse(BaseModel):
    institution_name: str
    active_role_profiles_count: int = 0
    total_evaluated_students: int = 0
    readiness_distribution: PlacementReadinessDistribution
    project_verification_summary: PlacementProjectVerificationSummary
    top_industry_skill_gaps: List[SkillGapItem] = Field(default_factory=list)
    freshness: DataFreshnessInfo


# =========================================================================
# 5. Super Admin Platform Overview Schemas
# =========================================================================

class SuperAdminOverviewResponse(BaseModel):
    total_institutions: int = 0
    active_institutions: int = 0
    total_users: int = 0
    users_by_role: Dict[str, int] = Field(default_factory=dict)
    module_health_status: Dict[str, str] = Field(default_factory=dict)
    database_connectivity: str = "connected"
    database_latency_ms: Optional[float] = None
    latest_migration: str = "bbd5b7842000"
    ai_service_configured: bool = False
    freshness: DataFreshnessInfo
