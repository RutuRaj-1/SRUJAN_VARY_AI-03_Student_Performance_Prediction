import pytest
import uuid
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
    CompetencyEvidenceState,
    CompetencyEvidenceType,
    CareerAlignmentStatus,
    CareerSkillGapType,
    CareerGapSeverity,
    ProjectVerificationStatus,
    RoleRequirementImportance,
    RoleMappingStatus,
)
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.academic_data import StudentAcademicProfile
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
)
from app.models.mastery import TopicMasteryResult
from app.models.career import (
    StudentProjectEvidence,
    StudentCompetencyEvidence,
    CareerReadinessAnalysis,
    CareerSkillGapFinding,
    CareerDevelopmentRecommendation,
)

# In-Memory SQLite Engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

INST_A_ID = uuid.uuid4()
INST_B_ID = uuid.uuid4()
FACULTY_A_ID = uuid.uuid4()
STUDENT_A_USER_ID = uuid.uuid4()
STUDENT_A_PROFILE_ID = uuid.uuid4()
STUDENT_B_USER_ID = uuid.uuid4()
STUDENT_B_PROFILE_ID = uuid.uuid4()
PLACEMENT_OFFICER_ID = uuid.uuid4()
ROLE_SDE_ID = uuid.uuid4()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Institutions
        inst_a = Institution(id=INST_A_ID, name="Apex Institute of Technology", institution_code="APEX-CR", city="Bangalore", state="Karnataka", is_active=True)
        inst_b = Institution(id=INST_B_ID, name="Beacon University", institution_code="BEACON-CR", city="Hyderabad", state="Telangana", is_active=True)
        db.add_all([inst_a, inst_b])

        # Profiles
        p_fac = Profile(id=FACULTY_A_ID, full_name="Dr. Alan Turing", email="faculty@apex.edu", role=UserRole.FACULTY.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_stu_a = Profile(id=STUDENT_A_USER_ID, full_name="Alice Smith", email="alice@apex.edu", role=UserRole.STUDENT.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        p_stu_b = Profile(id=STUDENT_B_USER_ID, full_name="Bob Jones", email="bob@beacon.edu", role=UserRole.STUDENT.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_B_ID)
        p_po = Profile(id=PLACEMENT_OFFICER_ID, full_name="Patricia Officer", email="placement@apex.edu", role=UserRole.PLACEMENT_OFFICER.value, account_status=AccountStatus.ACTIVE.value, institution_id=INST_A_ID)
        db.add_all([p_fac, p_stu_a, p_stu_b, p_po])

        # Programs
        prog_a = AcademicProgram(id=uuid.uuid4(), institution_id=INST_A_ID, name="B.Tech CS", code="BTECH-CS", duration_years=4)
        prog_b = AcademicProgram(id=uuid.uuid4(), institution_id=INST_B_ID, name="B.Tech IT", code="BTECH-IT", duration_years=4)
        db.add_all([prog_a, prog_b])

        # Student Academic Profiles
        sap_a = StudentAcademicProfile(
            id=STUDENT_A_PROFILE_ID,
            institution_id=INST_A_ID,
            profile_id=STUDENT_A_USER_ID,
            program_id=prog_a.id,
            enrollment_number="APEX-CS-2024-001",
            first_name="Alice",
            last_name="Smith",
            department="CSE",
            admission_year=2022,
            current_semester=5,
        )
        sap_b = StudentAcademicProfile(
            id=STUDENT_B_PROFILE_ID,
            institution_id=INST_B_ID,
            profile_id=STUDENT_B_USER_ID,
            program_id=prog_b.id,
            enrollment_number="BEACON-CS-2024-001",
            first_name="Bob",
            last_name="Jones",
            department="IT",
            admission_year=2022,
            current_semester=5,
        )
        db.add_all([sap_a, sap_b])

        # Career Role Profile (SDE Backend)
        role_sde = IndustryRoleProfile(
            id=ROLE_SDE_ID,
            role_title="Software Development Engineer - Backend",
            role_family="Software Development",
            description="Designs and implements scalable backend APIs, database schemas, and data pipelines.",
            experience_tier="Entry-Level / Fresher",
            version="1.0",
            is_active=True,
            review_status="APPROVED",
        )
        db.add(role_sde)

        # Requirements
        req_dsa = IndustryCompetencyRequirement(
            id=uuid.uuid4(),
            role_id=ROLE_SDE_ID,
            competency_name="Data Structures & Algorithms",
            category="ANALYTICAL",
            required_depth=4,
            importance="HIGH",
            mapping_status="APPROVED",
        )
        req_db = IndustryCompetencyRequirement(
            id=uuid.uuid4(),
            role_id=ROLE_SDE_ID,
            competency_name="Database Design & SQL Optimization",
            category="TOOLS_TECHNOLOGIES",
            required_depth=4,
            importance="HIGH",
            mapping_status="APPROVED",
        )
        req_api = IndustryCompetencyRequirement(
            id=uuid.uuid4(),
            role_id=ROLE_SDE_ID,
            competency_name="RESTful API Architecture",
            category="PRACTICAL",
            required_depth=4,
            importance="HIGH",
            mapping_status="APPROVED",
        )
        req_ai_unreviewed = IndustryCompetencyRequirement(
            id=uuid.uuid4(),
            role_id=ROLE_SDE_ID,
            competency_name="Distributed System Microservices",
            category="PRACTICAL",
            required_depth=3,
            importance="MEDIUM",
            mapping_status="AI_SUGGESTED",
        )
        db.add_all([req_dsa, req_db, req_api, req_ai_unreviewed])

        # Alice's Topic Mastery Evidence (DSA 85%) stored in StudentCompetencyEvidence
        ev_dsa = StudentCompetencyEvidence(
            id=uuid.uuid4(),
            institution_id=INST_A_ID,
            student_id=STUDENT_A_PROFILE_ID,
            competency_name="Data Structures & Algorithms",
            category="ANALYTICAL",
            evidence_type=CompetencyEvidenceType.TOPIC_MASTERY.value,
            source_entity_type="TOPIC_MASTERY_RESULT",
            source_entity_id=uuid.uuid4(),
            evidence_state=CompetencyEvidenceState.DEMONSTRATED.value,
            score_or_metric=85.0,
            evidence_summary="Demonstrated topic mastery of 85.0% across continuous assessments.",
            is_eligible=True,
        )
        db.add(ev_dsa)

        db.commit()
    finally:
        db.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_active_user, None)


def auth_as(user_id: uuid.UUID, role: UserRole, institution_id: uuid.UUID):
    def _override():
        return CurrentUser(
            user_id=str(user_id),
            email=f"{role.value.lower()}@test.edu",
            role=role,
            account_status=AccountStatus.ACTIVE,
            full_name=f"Test {role.value.title()}",
            institution_id=str(institution_id),
        )
    app.dependency_overrides[get_current_active_user] = _override


client = TestClient(app)


# =========================================================================
# Test Scenarios
# =========================================================================

def test_list_career_roles():
    """Verify that any authenticated user can list available active career role profiles."""
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    resp = client.get("/api/v1/career-readiness/roles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    sde_role = next((r for r in data if r["id"] == str(ROLE_SDE_ID)), None)
    assert sde_role is not None
    assert sde_role["role_title"] == "Software Development Engineer - Backend"
    assert len(sde_role["requirements"]) >= 4


def test_student_submit_project_and_faculty_verification():
    """Verify student practical project submission and faculty review workflow."""
    # 1. Student A submits practical project
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    proj_payload = {
        "title": "Inventory Management REST API",
        "description": "Full-stack inventory tracking system built with FastAPI and PostgreSQL.",
        "technology_stack": ["Python", "FastAPI", "PostgreSQL"],
        "repository_url": "https://github.com/alice/inventory-api",
        "demonstrated_competencies": ["RESTful API Architecture", "Database Design & SQL Optimization"],
    }
    resp = client.post("/api/v1/career-readiness/projects", json=proj_payload)
    assert resp.status_code == 201
    proj_data = resp.json()
    assert proj_data["title"] == "Inventory Management REST API"
    assert proj_data["verification_status"] == "PENDING_REVIEW"
    project_id = proj_data["id"]

    # 2. Student cannot review their own project
    review_payload = {
        "verification_status": "VERIFIED",
        "verification_notes": "Self approval should fail",
    }
    resp_bad = client.post(f"/api/v1/career-readiness/projects/{project_id}/review", json=review_payload)
    assert resp_bad.status_code == 403

    # 3. Faculty verifies project
    auth_as(FACULTY_A_ID, UserRole.FACULTY, INST_A_ID)
    review_payload = {
        "verification_status": "VERIFIED",
        "verification_notes": "Well architected OpenAPI endpoints with robust relational schema design.",
    }
    resp_review = client.post(f"/api/v1/career-readiness/projects/{project_id}/review", json=review_payload)
    assert resp_review.status_code == 200
    reviewed_proj = resp_review.json()
    assert reviewed_proj["verification_status"] == "VERIFIED"
    assert reviewed_proj["reviewer_id"] == str(FACULTY_A_ID)

    # 4. Check that Competency Evidence ledger now reflects DEMONSTRATED practical competencies
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    ev_resp = client.get("/api/v1/career-readiness/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    api_ev = next((e for e in ev_data if "RESTful API" in e["competency_name"]), None)
    assert api_ev is not None
    assert api_ev["evidence_state"] == "DEMONSTRATED"
    assert api_ev["evidence_type"] == "PROJECT_DEMONSTRATION"


def test_career_readiness_analysis_and_non_aggregation():
    """Verify role-specific readiness analysis adheres to non-aggregation principle (no single employability score)."""
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    req_body = {
        "role_id": str(ROLE_SDE_ID),
        "force_recalculate": True,
    }
    resp = client.post("/api/v1/career-readiness/analyze", json=req_body)
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis["role_id"] == str(ROLE_SDE_ID)
    # Check that alignment status is interpretable and non-aggregated
    assert analysis["alignment_status"] in (
        CareerAlignmentStatus.STRONG_EVIDENCE_ALIGNMENT.value,
        CareerAlignmentStatus.PARTIAL_EVIDENCE_ALIGNMENT.value,
    )
    assert "core_competency_coverage" in analysis
    assert "practical_evidence_coverage" in analysis
    assert analysis["demonstrated_count"] >= 2
    # Verify mandatory ethical disclaimer is present
    assert "disclaimer" in analysis
    assert "NOT constitute a guarantee of employment" in analysis["disclaimer"]


def test_categorized_skill_gaps_and_recommendations():
    """Verify that unreviewed AI mappings trigger MAPPING_GAP and actionable development recommendations are generated."""
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    resp = client.post("/api/v1/career-readiness/analyze", json={"role_id": str(ROLE_SDE_ID)})
    assert resp.status_code == 200
    analysis = resp.json()
    gap_findings = analysis["gap_findings"]

    # Verify MAPPING_GAP for unreviewed AI requirement
    mapping_gap = next((g for g in gap_findings if g["gap_type"] == CareerSkillGapType.MAPPING_GAP.value), None)
    assert mapping_gap is not None
    assert "Microservices" in mapping_gap["competency_name"]

    # Verify Career Development Recommendations
    recs = analysis["recommendations"]
    assert len(recs) >= 1
    assert "action_plan" in recs[0]
    assert "expected_evidence" in recs[0]


def test_placement_officer_firewall_and_readiness_access():
    """Verify Placement Officer can access authorized career readiness profiles, but is strictly barred from risk predictions & interventions."""
    # 1. Placement Officer accesses Career Readiness for Student A -> Allowed
    auth_as(PLACEMENT_OFFICER_ID, UserRole.PLACEMENT_OFFICER, INST_A_ID)
    resp_cr = client.post("/api/v1/career-readiness/analyze", json={
        "student_id": str(STUDENT_A_PROFILE_ID),
        "role_id": str(ROLE_SDE_ID),
    })
    assert resp_cr.status_code == 200
    assert resp_cr.json()["student_id"] == str(STUDENT_A_PROFILE_ID)

    # 2. Placement Officer attempts to access Academic Risk Predictions (Phase 07) -> FORBIDDEN (403)
    resp_risk = client.get(f"/api/v1/risk/students/{STUDENT_A_PROFILE_ID}/subjects/{uuid.uuid4()}/profile")
    assert resp_risk.status_code == 403

    # 3. Placement Officer attempts to access Confidential Academic Interventions (Phase 08) -> FORBIDDEN (403)
    resp_interv = client.get("/api/v1/interventions/plans")
    assert resp_interv.status_code == 403


def test_cross_student_isolation():
    """Verify Student B cannot modify or tamper with Student A's project evidence."""
    # Student A creates a project
    auth_as(STUDENT_A_USER_ID, UserRole.STUDENT, INST_A_ID)
    create_resp = client.post("/api/v1/career-readiness/projects", json={
        "title": "Private Microservice Project",
        "description": "Student A private project",
        "technology_stack": ["Go", "gRPC"],
        "demonstrated_competencies": ["API Architecture"],
    })
    assert create_resp.status_code == 201
    proj_id = create_resp.json()["id"]

    # Student B attempts to modify Student A's project -> Forbidden (403)
    auth_as(STUDENT_B_USER_ID, UserRole.STUDENT, INST_B_ID)
    tamper_resp = client.put(f"/api/v1/career-readiness/projects/{proj_id}", json={
        "title": "Tampered Title",
    })
    assert tamper_resp.status_code == 403
