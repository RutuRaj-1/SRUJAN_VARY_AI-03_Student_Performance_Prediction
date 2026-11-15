"""
Integration tests for Phase 10: Unified Intelligence Dashboard & Cross-Module Integration.
Tests role-aware dashboards (Student, Faculty, Institution Admin, Placement Officer, Super Admin),
RBAC and ownership boundaries, tenant isolation, and the strict Placement Officer firewall.
"""

import pytest
import uuid
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_current_active_user, CurrentUser
from app.models.enums import (
    UserRole,
    AccountStatus,
    MembershipRole,
    MembershipStatus,
    AssessmentType,
    AssessmentResultStatus,
    RecordVerificationStatus,
    AttendanceStatus,
    CareerAlignmentStatus,
    CareerGapSeverity,
    ProjectVerificationStatus,
)
from app.models.institution import Institution, InstitutionMembership
from app.models.profile import Profile
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
    AcademicDataQualityFinding,
)
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    IndustryRoleProfile,
)
from app.models.mastery import (
    MasteryAnalysisJob,
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)
from app.models.risk import (
    AcademicRiskTarget,
    AcademicRiskPrediction,
    AcademicRiskPredictionExplanation,
)
from app.models.interventions import (
    AcademicInterventionPlan,
    AcademicInterventionAction,
)
from app.models.career import (
    StudentProjectEvidence,
    CareerReadinessAnalysis,
    CareerSkillGapFinding,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Deterministic IDs
INST_A_ID = uuid.uuid4()
INST_B_ID = uuid.uuid4()
PROGRAM_ID = uuid.uuid4()
SUBJECT_ID = uuid.uuid4()

STUDENT_A_USER_ID = uuid.uuid4()
STUDENT_A_PROFILE_ID = uuid.uuid4()

STUDENT_B_USER_ID = uuid.uuid4()
STUDENT_B_PROFILE_ID = uuid.uuid4()

FACULTY_USER_ID = uuid.uuid4()
INST_ADMIN_USER_ID = uuid.uuid4()
PLACEMENT_USER_ID = uuid.uuid4()
SUPER_ADMIN_USER_ID = uuid.uuid4()

ROLE_ID = uuid.uuid4()
JOB_ID = uuid.uuid4()
TARGET_ID = uuid.uuid4()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # 1. Institutions
        inst_a = Institution(id=INST_A_ID, name="Apex Institute of Technology", institution_code="APEX-DASH", city="Bangalore", state="Karnataka", is_active=True)
        inst_b = Institution(id=INST_B_ID, name="Beacon University", institution_code="BEACON-DASH", city="Hyderabad", state="Telangana", is_active=True)
        db.add_all([inst_a, inst_b])

        # 2. Profiles
        p_stud_a = Profile(id=STUDENT_A_USER_ID, full_name="Aarav Sharma", email="aarav@apex.edu", role=UserRole.STUDENT.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_stud_b = Profile(id=STUDENT_B_USER_ID, full_name="Rohan Verma", email="rohan@apex.edu", role=UserRole.STUDENT.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_fac = Profile(id=FACULTY_USER_ID, full_name="Dr. Alan Turing", email="faculty@apex.edu", role=UserRole.FACULTY.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_admin = Profile(id=INST_ADMIN_USER_ID, full_name="Dean Administration", email="admin@apex.edu", role=UserRole.INSTITUTION_ADMIN.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_placement = Profile(id=PLACEMENT_USER_ID, full_name="Sarah Placement Officer", email="placement@apex.edu", role=UserRole.PLACEMENT_OFFICER.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_super = Profile(id=SUPER_ADMIN_USER_ID, full_name="System Super Admin", email="super@mastery.edu", role=UserRole.SUPER_ADMIN.value, account_status=AccountStatus.ACTIVE.value, institution_id=None)
        db.add_all([p_stud_a, p_stud_b, p_fac, p_admin, p_placement, p_super])

        # Memberships
        m_fac = InstitutionMembership(institution_id=INST_A_ID, user_id=FACULTY_USER_ID, membership_role=MembershipRole.FACULTY.value, membership_status=MembershipStatus.ACTIVE.value)
        db.add(m_fac)

        # 3. Programs and Subjects
        prog = AcademicProgram(id=PROGRAM_ID, institution_id=INST_A_ID, name="B.Tech Computer Science and Engineering", code="CSE", degree_type="BACHELORS", duration_years=4)
        subj = AcademicSubject(id=SUBJECT_ID, institution_id=INST_A_ID, program_id=PROGRAM_ID, name="Advanced Data Structures", code="CS301", semester=5)
        db.add_all([prog, subj])

        # 4. Student Academic Profiles
        sap_a = StudentAcademicProfile(
            id=STUDENT_A_PROFILE_ID,
            institution_id=INST_A_ID,
            profile_id=STUDENT_A_USER_ID,
            program_id=PROGRAM_ID,
            enrollment_number="APEX-CSE-2023-001",
            first_name="Aarav",
            last_name="Sharma",
            email="aarav@apex.edu",
            department="Computer Science & Engineering",
            admission_year=2023,
            current_semester=5,
            academic_status="ENROLLED",
        )
        sap_b = StudentAcademicProfile(
            id=STUDENT_B_PROFILE_ID,
            institution_id=INST_A_ID,
            profile_id=STUDENT_B_USER_ID,
            program_id=PROGRAM_ID,
            enrollment_number="APEX-CSE-2023-002",
            first_name="Rohan",
            last_name="Verma",
            email="rohan@apex.edu",
            department="Computer Science & Engineering",
            admission_year=2023,
            current_semester=5,
            academic_status="ENROLLED",
        )
        db.add_all([sap_a, sap_b])

        # 5. Enrollments & Academic Records
        enr = StudentSubjectEnrollment(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_ID, academic_year="2024-2025", semester=5)
        ass1 = AcademicAssessment(id=uuid.uuid4(), institution_id=INST_A_ID, subject_id=SUBJECT_ID, assessment_name="Mid-Term Test 1", academic_year="2024-2025", semester=5, assessment_type=AssessmentType.MID_TERM.value, maximum_marks=50.0)
        ass2 = AcademicAssessment(id=uuid.uuid4(), institution_id=INST_A_ID, subject_id=SUBJECT_ID, assessment_name="Mid-Term Test 2", academic_year="2024-2025", semester=5, assessment_type=AssessmentType.MID_TERM.value, maximum_marks=50.0)
        db.add_all([enr, ass1, ass2])
        db.flush()

        rec1 = StudentAssessmentRecord(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, assessment_id=ass1.id, marks_obtained=42.0, maximum_marks_snapshot=50.0, verification_status=RecordVerificationStatus.VERIFIED.value)
        rec2 = StudentAssessmentRecord(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, assessment_id=ass2.id, marks_obtained=35.0, maximum_marks_snapshot=50.0, verification_status=RecordVerificationStatus.IMPORTED.value)
        att = StudentAttendanceRecord(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_ID, academic_year="2024-2025", semester=5, attendance_date=datetime.now(timezone.utc), attendance_status=AttendanceStatus.PRESENT.value)
        db.add_all([rec1, rec2, att])

        # 6. Mastery
        job = MasteryAnalysisJob(id=JOB_ID, institution_id=INST_A_ID, subject_id=SUBJECT_ID, academic_year="2024-2025", semester=5, status="COMPLETED")
        db.add(job)
        db.flush()

        top_res1 = TopicMasteryResult(institution_id=INST_A_ID, analysis_job_id=JOB_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_ID, topic_id=uuid.uuid4(), mastery_percentage=85.0, mastery_status="DEMONSTRATED", evidence_sufficiency="SUFFICIENT")
        top_res2 = TopicMasteryResult(institution_id=INST_A_ID, analysis_job_id=JOB_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_ID, topic_id=uuid.uuid4(), mastery_percentage=45.0, mastery_status="DEVELOPING", evidence_sufficiency="PARTIAL")
        db.add_all([top_res1, top_res2])

        # 7. Risk
        target = AcademicRiskTarget(
            id=TARGET_ID,
            institution_id=INST_A_ID,
            subject_id=SUBJECT_ID,
            target_code="TARGET-CS301-FINAL",
            target_name="Semester End Exam Risk",
            outcome_definition="Scores below 50.0%",
            positive_label_definition="Scores < 50.0%",
            negative_label_definition="Scores >= 50.0%",
            passing_threshold_percentage=50.0,
            status="ACTIVE",
        )
        db.add(target)
        db.flush()

        pred = AcademicRiskPrediction(
            institution_id=INST_A_ID,
            student_id=STUDENT_A_PROFILE_ID,
            subject_id=SUBJECT_ID,
            target_id=TARGET_ID,
            risk_classification="MODERATE",
            risk_score=0.48,
            prediction_cutoff_date=datetime.now(timezone.utc),
        )
        db.add(pred)
        db.flush()

        exp1 = AcademicRiskPredictionExplanation(prediction_id=pred.id, feature_name="attendance_rate", feature_value=75.0, contribution_weight=0.35, explanation_text="Attendance near 75% threshold", is_adverse_factor=True)
        exp2 = AcademicRiskPredictionExplanation(prediction_id=pred.id, feature_name="internal_marks", feature_value=84.0, contribution_weight=0.25, explanation_text="Consistent mid-term performance", is_adverse_factor=False)
        db.add_all([exp1, exp2])

        # 8. Interventions
        plan = AcademicInterventionPlan(
            institution_id=INST_A_ID,
            student_id=STUDENT_A_PROFILE_ID,
            subject_id=SUBJECT_ID,
            plan_title="Algorithm Refinement & Problem Solving Support",
            learning_objective="Master tree and graph traversal algorithms",
            plan_status="ACTIVE",
            assigned_faculty_id=FACULTY_USER_ID,
        )
        db.add(plan)
        db.flush()

        act1 = AcademicInterventionAction(institution_id=INST_A_ID, plan_id=plan.id, action_title="Review BST Traversal", action_status="COMPLETED", instructions="Practice BST traversal problems")
        act2 = AcademicInterventionAction(institution_id=INST_A_ID, plan_id=plan.id, action_title="Solve 3 Graph Problems", action_status="PENDING", instructions="Solve 3 topological sort challenges")
        db.add_all([act1, act2])

        # 9. Career Readiness
        role = IndustryRoleProfile(id=ROLE_ID, institution_id=INST_A_ID, role_title="Backend Systems Engineer", role_family="Software Engineering", description="Designs scalable services", is_active=True)
        db.add(role)
        db.flush()

        analysis_id = uuid.uuid4()
        analysis = CareerReadinessAnalysis(
            id=analysis_id,
            institution_id=INST_A_ID,
            student_id=STUDENT_A_PROFILE_ID,
            role_id=ROLE_ID,
            alignment_status=CareerAlignmentStatus.PARTIAL_EVIDENCE_ALIGNMENT.value,
            core_competency_coverage=75.0,
            practical_evidence_coverage=60.0,
            summary_rationale="Student demonstrates strong theoretical basis and verified project implementation.",
        )
        proj = StudentProjectEvidence(
            institution_id=INST_A_ID,
            student_id=STUDENT_A_PROFILE_ID,
            title="High-Throughput Microservice",
            description="Distributed key-value store in Go",
            verification_status=ProjectVerificationStatus.VERIFIED.value,
            technology_stack=["Go", "gRPC", "Docker"],
            demonstrated_competencies=["Distributed Systems", "Concurrency"],
        )
        gap = CareerSkillGapFinding(
            institution_id=INST_A_ID,
            analysis_id=analysis_id,
            student_id=STUDENT_A_PROFILE_ID,
            role_id=ROLE_ID,
            competency_name="Distributed Consensus",
            gap_type="PRACTICAL_EVIDENCE_GAP",
            gap_severity=CareerGapSeverity.MODERATE.value,
            rationale="Theoretical knowledge demonstrated, but lacking practical implementation",
            suggested_action="Build a Raft consensus cluster in Go",
            evidence_needed="Working implementation with automated test suite",
        )
        db.add_all([analysis, proj, gap])

        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_dependencies():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


def auth_as(user_id: uuid.UUID, role: UserRole, institution_id: Optional[uuid.UUID] = INST_A_ID):
    user = CurrentUser(
        user_id=str(user_id),
        email=f"user_{user_id}@test.com",
        role=role,
        account_status=AccountStatus.ACTIVE,
        full_name=f"Test {role.value.title()}",
        institution_id=str(institution_id) if institution_id else None,
    )
    app.dependency_overrides[get_current_active_user] = lambda: user
    return TestClient(app)


# =========================================================================
# TEST SUITE
# =========================================================================

def test_student_dashboard_overview_and_ownership():
    """Student accesses their own unified dashboard; attempts to access peer's data receive 403."""
    client = auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)

    # 1. Own overview
    res = client.get("/api/v1/dashboard/student/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["student_profile"]["enrollment_number"] == "APEX-CSE-2023-001"
    assert data["student_profile"]["department"] == "Computer Science & Engineering"
    assert data["academic_performance"]["total_records"] == 2
    assert data["academic_performance"]["verified_records_count"] == 1
    assert data["academic_performance"]["average_marks"] == 84.0  # 42/50 * 100
    assert data["mastery_summary"]["topics_assessed_count"] == 2
    assert data["mastery_summary"]["topics_demonstrated_count"] == 1
    assert data["risk_summary"]["has_prediction"] is True
    assert data["risk_summary"]["risk_classification"] == "MODERATE"
    assert len(data["risk_summary"]["primary_adverse_factors"]) >= 1
    assert data["intervention_summary"]["active_plans_count"] == 1
    assert data["career_summary"]["target_role_title"] == "Backend Systems Engineer"
    assert data["career_summary"]["core_coverage_pct"] == 75.0
    assert data["career_summary"]["practical_coverage_pct"] == 60.0

    # 2. Student attempts to access Student B's overview -> 403 Forbidden
    res_forbidden = client.get(f"/api/v1/dashboard/student/overview?student_id={STUDENT_B_PROFILE_ID}")
    assert res_forbidden.status_code == 403


def test_faculty_dashboard_overview_and_queues():
    """Faculty accesses their overview with verification queues and cohort risk."""
    client = auth_as(FACULTY_USER_ID, UserRole.FACULTY, INST_A_ID)

    res = client.get("/api/v1/dashboard/faculty/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["faculty_name"] == "Dr. Alan Turing"
    assert len(data["assigned_subjects"]) >= 1
    assert data["verification_queue"]["pending_academic_records"] >= 1
    assert data["cohort_risk_overview"]["moderate_risk_students_count"] >= 1
    assert data["freshness"]["source_module"] == "Unified Dashboard Integration Layer"

    # Student attempting to access faculty dashboard receives 403
    stud_client = auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    stud_res = stud_client.get("/api/v1/dashboard/faculty/overview")
    assert stud_res.status_code == 403


def test_institution_admin_dashboard_overview():
    """Institution Admin accesses multi-dimensional institutional metrics."""
    client = auth_as(INST_ADMIN_USER_ID, UserRole.INSTITUTION_ADMIN, INST_A_ID)

    res = client.get("/api/v1/dashboard/institution/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["institution_name"] == "Apex Institute of Technology"
    assert data["summary_counts"]["total_active_students"] >= 1
    assert data["academic_data_status"]["total_academic_records"] >= 2
    assert data["risk_distribution"]["medium_risk_count"] >= 1
    assert data["intervention_metrics"]["active_plans_count"] >= 1
    assert data["career_readiness_overview"]["verified_projects_total"] >= 1

    # Student cannot access institution overview
    stud_client = auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    assert stud_client.get("/api/v1/dashboard/institution/overview").status_code == 403


def test_placement_officer_dashboard_and_firewall():
    """
    Placement Officer can view career readiness and skill gaps,
    but is strictly BLOCKED (403) from accessing academic risk or interventions.
    """
    client = auth_as(PLACEMENT_USER_ID, UserRole.PLACEMENT_OFFICER, INST_A_ID)

    # 1. Permitted: Placement Overview
    res = client.get("/api/v1/dashboard/placement/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["active_role_profiles_count"] >= 1
    assert data["readiness_distribution"]["approaching_count"] >= 1
    assert data["project_verification_summary"]["verified_projects_count"] >= 1
    assert len(data["top_industry_skill_gaps"]) >= 1

    # 2. FIREWALL ENFORCEMENT: Placement Officer blocked from Risk APIs
    risk_res = client.get(f"/api/v1/dashboard/student/risk-summary?student_id={STUDENT_A_PROFILE_ID}")
    assert risk_res.status_code == 403, "Placement Officer must be blocked from risk summary"

    # 3. FIREWALL ENFORCEMENT: Placement Officer blocked from Intervention APIs
    int_res = client.get(f"/api/v1/dashboard/student/intervention-summary?student_id={STUDENT_A_PROFILE_ID}")
    assert int_res.status_code == 403, "Placement Officer must be blocked from intervention summary"

    # 4. FIREWALL ENFORCEMENT: Placement Officer blocked from Student Overview (which embeds risk & interventions)
    over_res = client.get(f"/api/v1/dashboard/student/overview?student_id={STUDENT_A_PROFILE_ID}")
    assert over_res.status_code == 403, "Placement Officer must be blocked from full student overview"


def test_super_admin_dashboard_operational_telemetry():
    """Super Admin accesses multi-tenant telemetry, module health, and database latency."""
    client = auth_as(SUPER_ADMIN_USER_ID, UserRole.SUPER_ADMIN, None)

    res = client.get("/api/v1/dashboard/admin/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total_institutions"] >= 2
    assert data["total_users"] >= 5
    assert data["database_connectivity"] == "connected"
    assert "Module 08: Career Readiness & Industry Skill Gap" in data["module_health_status"]
    assert data["module_health_status"]["Module 06: Academic Risk Prediction Engine"] == "HEALTHY"

    # Faculty blocked from admin overview
    fac_client = auth_as(FACULTY_USER_ID, UserRole.FACULTY, INST_A_ID)
    assert fac_client.get("/api/v1/dashboard/admin/overview").status_code == 403


def test_data_freshness_and_non_aggregation():
    """Verifies that no arbitrary composite scores exist and metadata freshness is preserved."""
    client = auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    res = client.get("/api/v1/dashboard/student/overview")
    assert res.status_code == 200
    data = res.json()

    # Preserves separate core and practical coverage
    assert data["career_summary"]["core_coverage_pct"] is not None
    assert data["career_summary"]["practical_coverage_pct"] is not None
    assert "composite_score" not in data["career_summary"]

    # Freshness timestamps are present
    assert data["academic_performance"]["freshness"]["freshness_status"] in ("FRESH", "NOT_AVAILABLE")
    assert data["mastery_summary"]["freshness"]["source_module"] == "Module 05: Learning Mastery & Performance Analytics"
    assert "Academic risk predictions indicate potential difficulty" in data["risk_summary"]["disclaimer"]
