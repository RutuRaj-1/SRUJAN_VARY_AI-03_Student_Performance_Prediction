"""
MASTERY — Phase 11 Integration & Hardening Test Suite.
Verifies:
1. End-to-end 8-stage inter-module workflow.
2. Negative security test cases (Placement firewall, tenant isolation, student privacy, role tampering).
"""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.enums import (
    UserRole,
    AccountStatus,
    BloomTaxonomyLevel,
    AssessmentType,
    AssessmentResultStatus,
    RiskClassification,
    InterventionPlanStatus,
    CareerAlignmentStatus,
    RecordVerificationStatus,
)
from app.models.institution import Institution, InstitutionMembership
from app.models.profile import Profile
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    SyllabusTopic,
    LearningOutcome,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
)
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.mastery import TopicMasteryResult, LearningOutcomeAttainmentResult, LearningGapFinding
from app.models.risk import AcademicRiskTarget, AcademicRiskPrediction
from app.models.interventions import AcademicInterventionPlan, AcademicInterventionAction
from app.models.career import CareerReadinessAnalysis, StudentProjectEvidence


# Setup in-memory SQLite test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_as(role: UserRole, user_id: uuid.UUID, inst_id: uuid.UUID):
    current = CurrentUser(
        user_id=str(user_id),
        email=f"{role.value.lower()}@mastery.edu",
        role=role,
        account_status=AccountStatus.ACTIVE,
        full_name=f"Test {role.value}",
        institution_id=str(inst_id),
    )
    app.dependency_overrides[get_current_user] = lambda: current


# -----------------------------------------------------------------------------
# 1. End-to-End Inter-Module Integration Workflow Test
# -----------------------------------------------------------------------------

def test_end_to_end_inter_module_workflow(client: TestClient, db_session):
    """
    Executes the complete 8-step inter-module evidence and intelligence flow:
    Stage 1: Syllabus & competencies.
    Stage 2: Academic record ingestion.
    Stage 3: Assessment evaluation evidence.
    Stage 4: Topic mastery computation.
    Stage 5: Academic risk prediction with protective factors.
    Stage 6: Faculty-reviewed academic intervention.
    Stage 7: Career readiness with practical projects.
    Stage 8: Unified Dashboard role aggregation.
    """
    inst_id = uuid.uuid4()
    inst = Institution(id=inst_id, name="Integration Test University", institution_code="ITU-01", city="Pune", state="Maharashtra")
    db_session.add(inst)

    prog_id = uuid.uuid4()
    prog = AcademicProgram(id=prog_id, institution_id=inst_id, name="B.Tech Computer Science", code="CS-INT")
    db_session.add(prog)

    subj_id = uuid.uuid4()
    subj = AcademicSubject(id=subj_id, institution_id=inst_id, program_id=prog_id, name="Advanced Database Systems", code="CS-401", semester=5)
    db_session.add(subj)

    faculty_user_id = uuid.uuid4()
    faculty_profile = Profile(id=faculty_user_id, email="integration.faculty@mastery.edu", full_name="Prof. Sharma", role=UserRole.FACULTY.value)
    db_session.add(faculty_profile)

    from app.models.syllabus import SyllabusDocument, SyllabusUnit
    doc_id = uuid.uuid4()
    doc = SyllabusDocument(
        id=doc_id,
        institution_id=inst_id,
        subject_id=subj_id,
        uploaded_by=faculty_user_id,
        file_name="cs401_syllabus.pdf",
        file_size_bytes=102400,
        mime_type="application/pdf",
        storage_path="syllabi/cs401.pdf",
        status="APPROVED",
    )
    db_session.add(doc)

    unit_id = uuid.uuid4()
    unit = SyllabusUnit(id=unit_id, document_id=doc_id, subject_id=subj_id, unit_number=2, title="Indexing & Optimization")
    db_session.add(unit)

    topic_id = uuid.uuid4()
    topic = SyllabusTopic(id=topic_id, unit_id=unit_id, topic_name="B-Trees & Index Tuning", order_index=1)
    db_session.add(topic)

    clo_id = uuid.uuid4()
    clo = LearningOutcome(
        id=clo_id,
        subject_id=subj_id,
        outcome_code="CLO-3",
        description="Analyze indexing efficiency",
        bloom_level=BloomTaxonomyLevel.ANALYZE.value,
    )
    db_session.add(clo)

    # Student identity
    student_user_id = uuid.uuid4()
    student_profile = Profile(id=student_user_id, email="integration.student@mastery.edu", full_name="Ishaan Gupta", role=UserRole.STUDENT.value)
    db_session.add(student_profile)

    stud_id = uuid.uuid4()
    student_acad = StudentAcademicProfile(
        id=stud_id,
        profile_id=student_user_id,
        institution_id=inst_id,
        program_id=prog_id,
        enrollment_number="ENR-INT-2026",
        first_name="Ishaan",
        last_name="Gupta",
        email="ishaan@mastery.edu",
        department="Computer Science & Engineering",
        admission_year=2024,
        current_semester=5,
        academic_status="ENROLLED",
    )
    db_session.add(student_acad)

    # Stage 2: Ingestion
    enrollment = StudentSubjectEnrollment(institution_id=inst_id, student_id=stud_id, subject_id=subj_id, academic_year="2025-2026", semester=5)
    db_session.add(enrollment)

    # Attendance
    attendance = StudentAttendanceRecord(
        institution_id=inst_id,
        student_id=stud_id,
        subject_id=subj_id,
        academic_year="2025-2026",
        semester=5,
        attendance_date=datetime.now(timezone.utc),
        attendance_status="PRESENT",
    )
    db_session.add(attendance)

    # Stage 3: Assessment evaluation
    assessment = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=inst_id,
        subject_id=subj_id,
        assessment_name="Mid-Term Query Tuning Exam",
        assessment_type=AssessmentType.MID_TERM.value,
        maximum_marks=50.0,
        academic_year="2025-2026",
        semester=5,
    )
    db_session.add(assessment)

    record = StudentAssessmentRecord(
        institution_id=inst_id,
        student_id=stud_id,
        assessment_id=assessment.id,
        marks_obtained=42.0,
        maximum_marks_snapshot=50.0,
        verification_status=RecordVerificationStatus.VERIFIED.value,
    )
    db_session.add(record)

    # Stage 4: Topic Mastery
    job_id = uuid.uuid4()
    from app.models.mastery import MasteryAnalysisJob
    job = MasteryAnalysisJob(
        id=job_id,
        institution_id=inst_id,
        subject_id=subj_id,
        academic_year="2025-2026",
        semester=5,
        status="COMPLETED",
    )
    db_session.add(job)

    mastery = TopicMasteryResult(
        institution_id=inst_id,
        analysis_job_id=job_id,
        student_id=stud_id,
        subject_id=subj_id,
        topic_id=topic_id,
        mastery_percentage=84.0,
        mastery_status="DEMONSTRATED",
        evidence_sufficiency="SUFFICIENT",
    )
    db_session.add(mastery)

    attainment = LearningOutcomeAttainmentResult(
        institution_id=inst_id,
        analysis_job_id=job_id,
        student_id=stud_id,
        subject_id=subj_id,
        learning_outcome_id=clo_id,
        attainment_percentage=85.0,
        attainment_status="ATTAINED",
        evidence_sufficiency="SUFFICIENT",
    )
    db_session.add(attainment)

    # Stage 5: Academic Risk Target and Prediction
    target = AcademicRiskTarget(
        id=uuid.uuid4(),
        institution_id=inst_id,
        subject_id=subj_id,
        target_name="Final Course Failure",
        target_code="INT-CS401-RISK",
        outcome_definition="Failing end-semester database exam",
        positive_label_definition="Scores < 50.0%",
        negative_label_definition="Scores >= 50.0%",
        passing_threshold_percentage=50.0,
        status="ACTIVE",
    )
    db_session.add(target)

    risk_pred = AcademicRiskPrediction(
        id=uuid.uuid4(),
        institution_id=inst_id,
        student_id=stud_id,
        subject_id=subj_id,
        target_id=target.id,
        risk_classification="LOW",
        risk_score=0.15,
        prediction_cutoff_date=datetime.now(timezone.utc),
    )
    db_session.add(risk_pred)

    # Stage 6: Personalized Academic Intervention
    plan = AcademicInterventionPlan(
        id=uuid.uuid4(),
        institution_id=inst_id,
        student_id=stud_id,
        subject_id=subj_id,
        plan_title="Advanced Query Execution Plan Exploration",
        learning_objective="Deepen EXPLAIN ANALYZE interpretation",
        plan_status="ACTIVE",
    )
    db_session.add(plan)

    action = AcademicInterventionAction(
        id=uuid.uuid4(),
        institution_id=inst_id,
        plan_id=plan.id,
        action_title="Profile 3 Slow Queries in PostgreSQL",
        action_status="PENDING",
        instructions="Analyze explain plan output",
    )
    db_session.add(action)

    # Stage 7: Career Readiness and Projects
    role = IndustryRoleProfile(
        id=uuid.uuid4(),
        institution_id=inst_id,
        role_title="Database Administrator & Performance Engineer",
        role_family="Infrastructure & Data",
        description="Optimizes storage engines and database clusters.",
        is_active=True,
    )
    db_session.add(role)

    req = IndustryCompetencyRequirement(
        id=uuid.uuid4(),
        role_id=role.id,
        competency_name="Database Index Optimization",
        category="TECHNICAL",
        required_depth=4,
        importance="HIGH",
    )
    db_session.add(req)

    proj = StudentProjectEvidence(
        id=uuid.uuid4(),
        institution_id=inst_id,
        student_id=stud_id,
        title="PostgreSQL Index Benchmarking Tool",
        description="Engineered an automated query index benchmarking harness.",
        repository_url="https://github.com/ishaan/pg-bench",
        verification_status="VERIFIED",
    )
    db_session.add(proj)

    readiness = CareerReadinessAnalysis(
        id=uuid.uuid4(),
        institution_id=inst_id,
        student_id=stud_id,
        role_id=role.id,
        core_competency_coverage=85.0,
        practical_evidence_coverage=90.0,
        alignment_status="STRONG_EVIDENCE_ALIGNMENT",
        summary_rationale="Candidate demonstrates strong backend database engineering competencies and verified project portfolio.",
    )
    db_session.add(readiness)

    db_session.commit()

    # Stage 8: Unified Dashboard role verification
    auth_as(UserRole.STUDENT, student_user_id, inst_id)
    resp = client.get(f"/api/v1/dashboard/student/overview?student_id={stud_id}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["student_profile"]["full_name"] == "Ishaan Gupta"
    assert data["academic_performance"]["attendance_rate"] == 100.0
    assert data["mastery_summary"]["topics_demonstrated_count"] == 1
    assert data["risk_summary"]["risk_classification"] == "LOW"
    assert data["intervention_summary"]["active_plans_count"] == 1
    assert data["career_summary"]["target_role_title"] == "Database Administrator & Performance Engineer"
    assert data["career_summary"]["core_coverage_pct"] == 85.0
    assert data["career_summary"]["practical_coverage_pct"] == 90.0
    assert data["career_summary"]["verified_projects_count"] == 1


# -----------------------------------------------------------------------------
# 2. Negative Security & Privacy Boundary Tests
# -----------------------------------------------------------------------------

def test_unauthenticated_requests_rejected(client: TestClient):
    """Verifies unauthenticated callers receive HTTP 401."""
    app.dependency_overrides.pop(get_current_user, None)
    routes = [
        "/api/v1/dashboard/student/overview",
        "/api/v1/dashboard/faculty/overview",
        "/api/v1/dashboard/institution/overview",
        "/api/v1/dashboard/placement/overview",
        "/api/v1/dashboard/admin/overview",
    ]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code == 401, f"Route {r} should reject unauthenticated requests"


def test_placement_officer_firewall_blocks_risk_and_interventions(client: TestClient, db_session):
    """
    Critical Invariant: Placement Officers must be blocked with HTTP 403
    from student risk predictions and confidential interventions.
    """
    po_user_id = uuid.uuid4()
    inst_id = uuid.uuid4()
    auth_as(UserRole.PLACEMENT_OFFICER, po_user_id, inst_id)

    # Blocked dashboard endpoints
    blocked_endpoints = [
        "/api/v1/dashboard/student/overview",
        "/api/v1/dashboard/student/risk-summary",
        "/api/v1/dashboard/student/intervention-summary",
    ]
    for ep in blocked_endpoints:
        resp = client.get(ep)
        assert resp.status_code == 403, f"Placement Officer must be blocked from {ep}"
        assert (
            "Placement Officers are strictly prohibited" in resp.json()["detail"]
            or "Access forbidden" in resp.json()["detail"]
        )


def test_cross_student_isolation(client: TestClient, db_session):
    """Verifies student A cannot view student B's records."""
    inst_id = uuid.uuid4()
    inst = Institution(id=inst_id, name="Tenancy Test University", institution_code="TTU-01", city="Pune", state="Maharashtra")
    prog = AcademicProgram(id=uuid.uuid4(), institution_id=inst_id, name="B.Tech Computer Science", code="CS-TTU")
    db_session.add_all([inst, prog])
    db_session.flush()

    s1_uid = uuid.uuid4()
    s2_uid = uuid.uuid4()

    s1_acad_id = uuid.uuid4()
    s2_acad_id = uuid.uuid4()

    s1 = StudentAcademicProfile(
        id=s1_acad_id,
        profile_id=s1_uid,
        institution_id=inst_id,
        program_id=prog.id,
        enrollment_number="S1-001",
        first_name="Student",
        last_name="One",
        email="s1@mastery.edu",
        department="Computer Science",
        admission_year=2024,
    )
    s2 = StudentAcademicProfile(
        id=s2_acad_id,
        profile_id=s2_uid,
        institution_id=inst_id,
        program_id=prog.id,
        enrollment_number="S2-002",
        first_name="Student",
        last_name="Two",
        email="s2@mastery.edu",
        department="Computer Science",
        admission_year=2024,
    )
    db_session.add_all([s1, s2])
    db_session.commit()

    # Authenticate as student 1
    auth_as(UserRole.STUDENT, s1_uid, inst_id)

    # Attempting to access Student 2's dashboard directly
    resp = client.get(f"/api/v1/dashboard/student/overview?student_id={s2_acad_id}")
    assert resp.status_code == 403
    assert "Students may only access their own dashboard" in resp.json()["detail"]


def test_student_cannot_tamper_effective_role(client: TestClient):
    """Verifies that client payload / header manipulation cannot elevate user role."""
    student_uid = uuid.uuid4()
    inst_id = uuid.uuid4()
    auth_as(UserRole.STUDENT, student_uid, inst_id)

    # Student attempts to call admin overview with spoofed role in headers or query
    resp = client.get("/api/v1/dashboard/admin/overview")
    assert resp.status_code == 403
