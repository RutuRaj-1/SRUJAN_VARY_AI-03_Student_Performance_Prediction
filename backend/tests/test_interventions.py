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
    InterventionType,
    InterventionPriority,
    InterventionPlanStatus,
    InterventionActionStatus,
    InterventionRecommendationStatus,
    EvidenceSufficiencyLevel,
    RiskClassification,
)
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.syllabus import AcademicProgram, AcademicSubject, SyllabusDocument, SyllabusUnit, SyllabusTopic
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.mastery import MasteryAnalysisJob, TopicMasteryResult, LearningGapFinding
from app.models.risk import AcademicRiskTarget, AcademicRiskPrediction
from app.models.interventions import (
    InterventionTemplate,
    AcademicInterventionRecommendation,
    AcademicInterventionPlan,
    AcademicInterventionAction,
    InterventionProgressEvent,
    InterventionOutcomeObservation,
)

# Dedicated In-Memory SQLite Engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

INST_A_ID = uuid.uuid4()
ADMIN_A_ID = uuid.uuid4()
FACULTY_A_ID = uuid.uuid4()
STUDENT_A_USER_ID = uuid.uuid4()
STUDENT_A_PROFILE_ID = uuid.uuid4()
STUDENT_B_USER_ID = uuid.uuid4()
STUDENT_B_PROFILE_ID = uuid.uuid4()
PLACEMENT_USER_ID = uuid.uuid4()
PROGRAM_A_ID = uuid.uuid4()
SUBJECT_A_ID = uuid.uuid4()
TOPIC_1_ID = uuid.uuid4()
TOPIC_2_ID = uuid.uuid4()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Institution
    inst_a = Institution(id=INST_A_ID, name="Apex Institute of Technology", institution_code="AIT", city="Pune", state="Maharashtra")
    session.add(inst_a)

    # Profiles
    admin = Profile(id=ADMIN_A_ID, full_name="Admin Smith", email="admin@ait.edu", role=UserRole.INSTITUTION_ADMIN.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    fac = Profile(id=FACULTY_A_ID, full_name="Prof. Knuth", email="knuth@ait.edu", role=UserRole.FACULTY.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_a = Profile(id=STUDENT_A_USER_ID, full_name="Ada Lovelace", email="ada@ait.edu", role=UserRole.STUDENT.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_b = Profile(id=STUDENT_B_USER_ID, full_name="Charles Babbage", email="charles@ait.edu", role=UserRole.STUDENT.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    placement_user = Profile(id=PLACEMENT_USER_ID, full_name="Officer Vance", email="vance@ait.edu", role=UserRole.PLACEMENT_OFFICER.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    session.add_all([admin, fac, stud_user_a, stud_user_b, placement_user])

    # Program & Subject
    prog = AcademicProgram(id=PROGRAM_A_ID, institution_id=INST_A_ID, name="B.Tech CS", code="BTECH-CS", duration_years=4)
    subj = AcademicSubject(id=SUBJECT_A_ID, institution_id=INST_A_ID, program_id=PROGRAM_A_ID, name="Distributed Systems", code="CS401", semester=7, academic_year="2026-2027")
    session.add_all([prog, subj])

    # Syllabus
    doc = SyllabusDocument(id=uuid.uuid4(), institution_id=INST_A_ID, subject_id=SUBJECT_A_ID, file_name="cs401.pdf", file_size_bytes=1024, mime_type="application/pdf", storage_path="/uploads/cs401.pdf", status="APPROVED")
    session.add(doc)

    unit = SyllabusUnit(id=uuid.uuid4(), document_id=doc.id, subject_id=SUBJECT_A_ID, unit_number=1, title="Consensus Protocols", estimated_hours=12)
    session.add(unit)

    t1 = SyllabusTopic(id=TOPIC_1_ID, unit_id=unit.id, topic_name="Paxos Consensus", order_index=1)
    t2 = SyllabusTopic(id=TOPIC_2_ID, unit_id=unit.id, topic_name="Raft Consensus", order_index=2)
    session.add_all([t1, t2])

    # Student Academic Profiles
    stud_a = StudentAcademicProfile(id=STUDENT_A_PROFILE_ID, institution_id=INST_A_ID, profile_id=STUDENT_A_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2026-CSE-001", first_name="Ada", last_name="Lovelace", department="CSE", admission_year=2023, current_semester=7)
    stud_b = StudentAcademicProfile(id=STUDENT_B_PROFILE_ID, institution_id=INST_A_ID, profile_id=STUDENT_B_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2026-CSE-002", first_name="Charles", last_name="Babbage", department="CSE", admission_year=2023, current_semester=7)
    session.add_all([stud_a, stud_b])

    # Enrollments
    enr_a = StudentSubjectEnrollment(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_A_ID, academic_year="2026-2027", semester=7, enrollment_status="ACTIVE")
    enr_b = StudentSubjectEnrollment(institution_id=INST_A_ID, student_id=STUDENT_B_PROFILE_ID, subject_id=SUBJECT_A_ID, academic_year="2026-2027", semester=7, enrollment_status="ACTIVE")
    session.add_all([enr_a, enr_b])

    session.commit()
    session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_current_user(user_id: uuid.UUID, role: UserRole, email: str = "user@ait.edu") -> CurrentUser:
    return CurrentUser(
        user_id=str(user_id),
        email=email,
        role=role,
        account_status=AccountStatus.ACTIVE,
        full_name="Test User",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(FACULTY_A_ID, UserRole.FACULTY)
    yield
    app.dependency_overrides.clear()


# =========================================================================
# TEST SCENARIOS
# =========================================================================

def test_template_catalog_seeding_and_retrieval():
    """
    Verifies that default institutional templates are seeded on demand and can be retrieved.
    """
    client = TestClient(app)
    res = client.get("/api/v1/interventions/templates")
    assert res.status_code == 200, res.text
    templates = res.json()
    assert len(templates) >= 4
    codes = [t["template_code"] for t in templates]
    assert "TPL_TOPIC_REVISION" in codes
    assert "TPL_DIAGNOSTIC_EVAL" in codes


def test_recommendation_generation_for_verified_topic_gap():
    """
    Verifies that a student with a verified Phase 06 learning gap receives a targeted recommendation.
    """
    session = TestingSessionLocal()
    job = MasteryAnalysisJob(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        academic_year="2026-2027",
        semester=7,
        status="COMPLETED",
    )
    session.add(job)

    gap = LearningGapFinding(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        analysis_job_id=job.id,
        student_id=STUDENT_A_PROFILE_ID,
        subject_id=SUBJECT_A_ID,
        topic_id=TOPIC_1_ID,
        finding_type="PERSISTENT_LOW_SCORE",
        severity="HIGH",
        evidence_summary="Continuous failure across 2 midterm tests on Paxos.",
        status="OPEN",
    )
    session.add(gap)
    session.commit()
    session.close()

    client = TestClient(app)
    res = client.post(
        "/api/v1/interventions/recommendations/generate",
        json={"student_id": str(STUDENT_A_PROFILE_ID), "subject_id": str(SUBJECT_A_ID)},
    )
    assert res.status_code == 200, res.text
    recs = res.json()
    assert len(recs) >= 1

    gap_rec = next((r for r in recs if r["topic_id"] == str(TOPIC_1_ID)), None)
    assert gap_rec is not None
    assert gap_rec["recommendation_type"] == "TARGETED_REVISION"
    assert gap_rec["priority"] == "HIGH"
    assert "Paxos" in gap_rec["proposed_action_title"]
    assert "scientific_disclaimer" in gap_rec


def test_insufficient_evidence_recommendation_handling():
    """
    Verifies that when a student has insufficient assessment evidence, the engine outputs
    a low-stakes diagnostic exercise rather than a punitive remedial intervention.
    """
    session = TestingSessionLocal()
    # Student B has zero assessment records. Add an INSUFFICIENT_EVIDENCE risk prediction
    target = AcademicRiskTarget(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        target_code="INSUF_TGT",
        target_name="Course Final Target",
        outcome_definition="Scores < 50%",
        positive_label_definition="< 50%",
        negative_label_definition=">= 50%",
    )
    pred = AcademicRiskPrediction(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        target_id=target.id,
        model_version_id=uuid.uuid4(),
        student_id=STUDENT_B_PROFILE_ID,
        subject_id=SUBJECT_A_ID,
        prediction_cutoff_date=datetime.now(timezone.utc),
        risk_score=None,
        risk_classification=RiskClassification.INSUFFICIENT_EVIDENCE.value,
        evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
        prediction_status="ACTIVE",
        scientific_disclaimer="Disclaimer",
    )
    session.add_all([target, pred])
    session.commit()
    session.close()

    client = TestClient(app)
    res = client.post(
        "/api/v1/interventions/recommendations/generate",
        json={"student_id": str(STUDENT_B_PROFILE_ID), "subject_id": str(SUBJECT_A_ID)},
    )
    assert res.status_code == 200, res.text
    recs = res.json()
    assert len(recs) >= 1

    insuf_rec = recs[0]
    assert insuf_rec["recommendation_type"] == InterventionType.FORMATIVE_ASSESSMENT.value
    assert insuf_rec["evidence_sufficiency"] == "INSUFFICIENT"
    assert "insufficient" in insuf_rec["rationale"].lower()


def test_plan_lifecycle_approval_and_completion():
    """
    Verifies full plan lifecycle:
    Authoring (DRAFT/PENDING_REVIEW) -> Faculty Approval (APPROVED) -> Assignment (ACTIVE)
    -> Action Submission (SUBMITTED) -> Faculty Verification (VERIFIED) -> Plan Auto-Completion (COMPLETED).
    """
    client = TestClient(app)

    # 1. Author Plan
    plan_payload = {
        "student_id": str(STUDENT_A_PROFILE_ID),
        "subject_id": str(SUBJECT_A_ID),
        "topic_id": str(TOPIC_1_ID),
        "plan_title": "Paxos Consensus Mastery Acceleration",
        "learning_objective": "Attain minimum 70% demonstrated understanding on Paxos algorithmic phases.",
        "target_completion_date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
        "expected_outcome_evidence": "Verification quiz submission and lab practice logs",
    }
    create_res = client.post("/api/v1/interventions/plans", json=plan_payload)
    assert create_res.status_code == 200, create_res.text
    plan_data = create_res.json()
    plan_id = plan_data["id"]
    assert plan_data["plan_status"] == InterventionPlanStatus.PENDING_REVIEW.value
    assert len(plan_data["actions"]) >= 1
    action_id = plan_data["actions"][0]["id"]

    # 2. Faculty Approves Plan
    review_res = client.post(
        f"/api/v1/interventions/plans/{plan_id}/review",
        json={"decision": "APPROVE", "review_notes": "Authorized pedagogical recovery plan."},
    )
    assert review_res.status_code == 200
    assert review_res.json()["plan_status"] == InterventionPlanStatus.APPROVED.value

    # 3. Faculty Assigns Plan
    assign_res = client.post(f"/api/v1/interventions/plans/{plan_id}/assign")
    assert assign_res.status_code == 200
    assert assign_res.json()["plan_status"] == InterventionPlanStatus.ACTIVE.value

    # 4. Student Starts Action
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(STUDENT_A_USER_ID, UserRole.STUDENT)
    start_res = client.post(
        f"/api/v1/interventions/actions/{action_id}/status",
        json={"new_status": "IN_PROGRESS"},
    )
    assert start_res.status_code == 200
    assert start_res.json()["action_status"] == "IN_PROGRESS"

    # 5. Student Submits Evidence
    submit_res = client.post(
        f"/api/v1/interventions/actions/{action_id}/status",
        json={
            "new_status": "SUBMITTED",
            "student_completion_notes": "Completed consensus protocol simulation and documented leader election edge cases.",
            "student_submission_url": "https://github.com/ait-cs/paxos-lab-solution",
        },
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["action_status"] == "SUBMITTED"

    # 6. Faculty Verifies Completion
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(FACULTY_A_ID, UserRole.FACULTY)
    verify_res = client.post(
        f"/api/v1/interventions/actions/{action_id}/status",
        json={"new_status": "VERIFIED", "faculty_feedback": "Excellent simulation and comprehensive edge case analysis."},
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["action_status"] == "VERIFIED"

    # 7. Plan Auto-Completed
    plan_final = client.get(f"/api/v1/interventions/plans/{plan_id}").json()
    assert plan_final["plan_status"] == InterventionPlanStatus.COMPLETED.value
    assert len(plan_final["progress_events"]) >= 5


def test_post_intervention_outcome_observation():
    """
    Verifies post-intervention evidence observation recording without unsupported causal claims.
    """
    client = TestClient(app)

    # Fetch existing plan from database
    session = TestingSessionLocal()
    plan = session.query(AcademicInterventionPlan).first()
    plan_id = str(plan.id)
    session.close()

    payload = {
        "baseline_mastery_percentage": 35.0,
        "followup_score_obtained": 18.0,
        "followup_maximum_marks": 20.0,
        "observation_notes": "Follow-up formative quiz on Paxos demonstrated 90% attainment.",
    }
    res = client.post(f"/api/v1/interventions/plans/{plan_id}/outcomes", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["baseline_mastery_percentage"] == 35.0
    assert data["followup_mastery_percentage"] == 90.0
    assert "scientific_disclaimer" in data


def test_security_rbac_and_placement_officer_boundary():
    """
    Verifies that:
    1. Students cannot access other students' intervention plans (403 Forbidden).
    2. Placement Officers are barred from all intervention endpoints (403 Forbidden).
    3. Students cannot approve their own plans (403 Forbidden).
    """
    client = TestClient(app)
    session = TestingSessionLocal()
    plan = session.query(AcademicInterventionPlan).filter(AcademicInterventionPlan.student_id == STUDENT_A_PROFILE_ID).first()
    plan_id = str(plan.id)
    session.close()

    # 1. Student B attempts to query Student A's plan -> 403 Forbidden
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(STUDENT_B_USER_ID, UserRole.STUDENT)
    res_peer = client.get(f"/api/v1/interventions/plans/{plan_id}")
    assert res_peer.status_code == 403

    # 2. Placement Officer attempts to access templates/plans -> 403 Forbidden
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(PLACEMENT_USER_ID, UserRole.PLACEMENT_OFFICER)
    res_placement = client.get("/api/v1/interventions/templates")
    assert res_placement.status_code == 403

    res_placement_plans = client.get("/api/v1/interventions/plans")
    assert res_placement_plans.status_code == 403

    # 3. Student A attempts to approve plan -> 403 Forbidden
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(STUDENT_A_USER_ID, UserRole.STUDENT)
    res_stud_approve = client.post(
        f"/api/v1/interventions/plans/{plan_id}/review",
        json={"decision": "APPROVE"},
    )
    assert res_stud_approve.status_code == 403
