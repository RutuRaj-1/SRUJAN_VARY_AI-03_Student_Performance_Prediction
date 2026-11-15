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
from app.models.enums import UserRole, AccountStatus, MasteryStatus, LearningGapSeverity, RiskClassification
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
from app.models.assessment import AssessmentAttempt
from app.models.mastery import MasteryAnalysisJob, TopicMasteryResult, LearningGapFinding
from app.models.risk import AcademicRiskTarget, RiskModelVersion, AcademicRiskPrediction

# Dedicated In-Memory SQLite Engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

INST_A_ID = uuid.uuid4()
INST_B_ID = uuid.uuid4()
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

    # Institutions
    inst_a = Institution(id=INST_A_ID, name="Apex Institute of Technology", institution_code="AIT", city="Pune", state="Maharashtra")
    inst_b = Institution(id=INST_B_ID, name="Metropolitan Tech", institution_code="MTECH", city="Mumbai", state="Maharashtra")
    session.add_all([inst_a, inst_b])

    # Users
    admin = Profile(id=ADMIN_A_ID, full_name="Admin Smith", email="admin@ait.edu", role=UserRole.INSTITUTION_ADMIN.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    fac = Profile(id=FACULTY_A_ID, full_name="Prof. Knuth", email="knuth@ait.edu", role=UserRole.FACULTY.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_a = Profile(id=STUDENT_A_USER_ID, full_name="Ada Lovelace", email="ada@ait.edu", role=UserRole.STUDENT.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_b = Profile(id=STUDENT_B_USER_ID, full_name="Charles Babbage", email="charles@ait.edu", role=UserRole.STUDENT.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    placement_user = Profile(id=PLACEMENT_USER_ID, full_name="Officer Vance", email="vance@ait.edu", role=UserRole.PLACEMENT_OFFICER.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    session.add_all([admin, fac, stud_user_a, stud_user_b, placement_user])

    # Program, Subject & Syllabus
    prog = AcademicProgram(id=PROGRAM_A_ID, institution_id=INST_A_ID, name="B.Tech CS", code="BTECH-CS", duration_years=4)
    subj = AcademicSubject(id=SUBJECT_A_ID, institution_id=INST_A_ID, program_id=PROGRAM_A_ID, name="Distributed Systems", code="CS401", semester=7, academic_year="2026-2027")
    session.add_all([prog, subj])

    doc = SyllabusDocument(id=uuid.uuid4(), institution_id=INST_A_ID, subject_id=SUBJECT_A_ID, file_name="cs401_syllabus.pdf", file_size_bytes=1024, mime_type="application/pdf", storage_path="/uploads/cs401.pdf", status="APPROVED")
    session.add(doc)

    unit = SyllabusUnit(id=uuid.uuid4(), document_id=doc.id, subject_id=SUBJECT_A_ID, unit_number=1, title="Consensus Algorithms", estimated_hours=12)
    session.add(unit)

    topic1 = SyllabusTopic(id=TOPIC_1_ID, unit_id=unit.id, topic_name="Paxos and Raft Consensus", order_index=1)
    topic2 = SyllabusTopic(id=TOPIC_2_ID, unit_id=unit.id, topic_name="Vector Clocks & Causality", order_index=2)
    session.add_all([topic1, topic2])

    # Students Academic Profiles
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

def test_target_configuration_and_institutional_threshold():
    """
    Verifies academic risk target creation, institutional threshold configuration, and retrieval.
    """
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(ADMIN_A_ID, UserRole.INSTITUTION_ADMIN)
    client = TestClient(app)

    payload = {
        "subject_id": str(SUBJECT_A_ID),
        "target_code": "MIDTERM_DEFICIT_45",
        "target_name": "Midterm Critical Deficit (<45%)",
        "outcome_definition": "Midterm verified score below 45.0%",
        "positive_label_definition": "Marks < 45.0%",
        "negative_label_definition": "Marks >= 45.0%",
        "passing_threshold_percentage": 45.0,
        "prediction_horizon_weeks": 3,
        "is_institution_policy": True,
    }
    res = client.post("/api/v1/risk/targets", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["target_code"] == "MIDTERM_DEFICIT_45"
    assert data["passing_threshold_percentage"] == 45.0
    assert data["status"] == "ACTIVE"

    list_res = client.get(f"/api/v1/risk/targets?subject_id={SUBJECT_A_ID}")
    assert list_res.status_code == 200
    targets = list_res.json()
    assert any(t["target_code"] == "MIDTERM_DEFICIT_45" for t in targets)


def test_temporal_leakage_prevention():
    """
    Verifies that records verified after observation cutoff or final exam scores
    are strictly barred from model feature vectors.
    """
    from app.services.risk.feature_service import risk_feature_service

    session = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)

    asmt_past = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Quiz 1",
        assessment_type="QUIZ",
        academic_year="2026-2027",
        semester=7,
        maximum_marks=20.0,
        passing_marks=8.0,
        status="PUBLISHED",
    )
    asmt_future = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Quiz 2",
        assessment_type="QUIZ",
        academic_year="2026-2027",
        semester=7,
        maximum_marks=20.0,
        passing_marks=8.0,
        status="PUBLISHED",
    )
    asmt_final = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Final Examination",
        assessment_type="FINAL_EXAM",
        academic_year="2026-2027",
        semester=7,
        maximum_marks=100.0,
        passing_marks=40.0,
        status="PUBLISHED",
    )
    session.add_all([asmt_past, asmt_future, asmt_final])

    # 1. Past continuous assessment (before cutoff) -> 16/20 = 80.0%
    rec_past = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=STUDENT_A_PROFILE_ID,
        assessment_id=asmt_past.id,
        maximum_marks_snapshot=20.0,
        marks_obtained=16.0,
        recorded_at=cutoff - timedelta(days=3),
        verification_status="VERIFIED",
    )
    # 2. Future continuous assessment (after cutoff - LEAKAGE CANDIDATE)
    rec_future = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=STUDENT_A_PROFILE_ID,
        assessment_id=asmt_future.id,
        maximum_marks_snapshot=20.0,
        marks_obtained=6.0,
        recorded_at=now,
        verification_status="VERIFIED",
    )
    # 3. Final Exam (TARGET LEAKAGE CANDIDATE)
    rec_final = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=STUDENT_A_PROFILE_ID,
        assessment_id=asmt_final.id,
        maximum_marks_snapshot=100.0,
        marks_obtained=35.0,
        recorded_at=cutoff - timedelta(days=1),
        verification_status="VERIFIED",
    )
    session.add_all([rec_past, rec_future, rec_final])
    session.commit()

    snapshot = risk_feature_service.extract_student_features(
        db=session,
        institution_id=INST_A_ID,
        student_id=STUDENT_A_PROFILE_ID,
        subject_id=SUBJECT_A_ID,
        cutoff_date=cutoff,
    )

    # Feature must reflect Quiz 1 (80%) and MUST NOT include future Quiz 2 or Final Exam
    assert snapshot.feature_vector_json["continuous_assessment_average"] == 80.0
    assert "final_exam_marks" not in snapshot.feature_vector_json
    session.close()


def test_insufficient_evidence_preservation():
    """
    Verifies that when a student has fewer than 2 continuous assessment records,
    the engine outputs INSUFFICIENT_EVIDENCE classification rather than assuming failure.
    """
    client = TestClient(app)
    session = TestingSessionLocal()

    target = AcademicRiskTarget(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        target_code="INSUFFICIENT_TEST_TARGET",
        target_name="Course Final Grade Deficit",
        outcome_definition="Scores below 50.0%",
        positive_label_definition="Scores < 50.0%",
        negative_label_definition="Scores >= 50.0%",
        passing_threshold_percentage=50.0,
        status="ACTIVE",
    )
    session.add(target)
    session.commit()

    # Student B has 0 continuous assessments
    gen_payload = {
        "subject_id": str(SUBJECT_A_ID),
        "target_id": str(target.id),
        "target_student_id": str(STUDENT_B_PROFILE_ID),
    }
    res = client.post("/api/v1/risk/predictions/generate", json=gen_payload)
    assert res.status_code == 200, res.text
    preds = res.json()
    assert len(preds) == 1
    pred = preds[0]
    assert pred["risk_classification"] == RiskClassification.INSUFFICIENT_EVIDENCE.value
    assert pred["risk_score"] is None
    assert pred["evidence_sufficiency"] == "INSUFFICIENT"
    assert len(pred["explanations"]) >= 1
    assert "insufficient" in pred["explanations"][0]["explanation_text"].lower()
    session.close()


def test_model_readiness_gate_and_rule_fallback():
    """
    Verifies that dataset readiness gate reports MODEL_NOT_READY when labeled data is insufficient,
    and falls back to deterministic rule baseline without generating fictitious probabilities.
    """
    client = TestClient(app)

    res = client.get(f"/api/v1/risk/readiness?subject_id={SUBJECT_A_ID}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["is_dataset_ready_for_training"] is False
    assert len(data["readiness_notes"]) >= 1

    # Train model when dataset is not ready -> auto fallback to DETERMINISTIC_RULES
    target_id = data["target_id"]
    train_res = client.post(
        f"/api/v1/risk/models/train?subject_id={SUBJECT_A_ID}",
        json={
            "target_id": target_id,
            "model_type": "LOGISTIC_REGRESSION",
            "version_tag": "test-auto-fallback-v1",
        },
    )
    assert train_res.status_code == 200, train_res.text
    model_data = train_res.json()
    assert model_data["model_type"] == "DETERMINISTIC_RULES"
    assert model_data["is_active"] is True


def test_prediction_explainability_and_grounding():
    """
    Verifies that risk prediction outputs grounded feature attributions and adverse factors
    derived strictly from verified student performance records.
    """
    session = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    # Create isolated student with acute academic risk indicators
    stud_c_user_id = uuid.uuid4()
    stud_c_profile_id = uuid.uuid4()
    user_c = Profile(
        id=stud_c_user_id,
        full_name="Risk Test Student",
        email="risk_stud@ait.edu",
        role=UserRole.STUDENT.value,
        institution_id=INST_A_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    stud_c = StudentAcademicProfile(
        id=stud_c_profile_id,
        profile_id=stud_c_user_id,
        institution_id=INST_A_ID,
        program_id=PROGRAM_A_ID,
        enrollment_number="ENR-RISK-01",
        first_name="Risk",
        last_name="Student",
        department="CSE",
        current_semester=7,
        admission_year=2023,
    )
    enr_c = StudentSubjectEnrollment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=stud_c_profile_id,
        subject_id=SUBJECT_A_ID,
        academic_year="2026-2027",
        semester=7,
        enrollment_status="ACTIVE",
    )
    session.add_all([user_c, stud_c, enr_c])

    # Add verified continuous assessment records showing deficit
    asmt_mid = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Midterm Exam 1",
        assessment_type="MIDTERM",
        academic_year="2026-2027",
        semester=7,
        maximum_marks=50.0,
        passing_marks=20.0,
        status="PUBLISHED",
    )
    asmt_lab = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Lab Test 1",
        assessment_type="LAB_EXAM",
        academic_year="2026-2027",
        semester=7,
        maximum_marks=25.0,
        passing_marks=10.0,
        status="PUBLISHED",
    )
    session.add_all([asmt_mid, asmt_lab])

    rec1 = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=stud_c_profile_id,
        assessment_id=asmt_mid.id,
        maximum_marks_snapshot=50.0,
        marks_obtained=18.0,  # 36.0% (Critical continuous deficit)
        recorded_at=now - timedelta(days=10),
        verification_status="VERIFIED",
    )
    rec2 = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=stud_c_profile_id,
        assessment_id=asmt_lab.id,
        maximum_marks_snapshot=25.0,
        marks_obtained=9.0,  # 36.0%
        recorded_at=now - timedelta(days=5),
        verification_status="VERIFIED",
    )
    # Add an analysis job and unresolved high-severity learning gap
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
        student_id=stud_c_profile_id,
        subject_id=SUBJECT_A_ID,
        topic_id=TOPIC_1_ID,
        finding_type="PERSISTENT_LOW_SCORE",
        severity=LearningGapSeverity.CRITICAL.value,
        evidence_summary="Persistent failure in Paxos Consensus algorithms.",
        status="OPEN",
    )
    # Low attendance
    att1 = StudentAttendanceRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=stud_c_profile_id,
        subject_id=SUBJECT_A_ID,
        academic_year="2026-2027",
        semester=7,
        attendance_date=now - timedelta(days=2),
        attendance_status="ABSENT",
        verification_status="VERIFIED",
    )
    session.add_all([rec1, rec2, gap, att1])
    session.commit()

    client = TestClient(app)
    target = AcademicRiskTarget(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        target_code="EXPLAIN_TEST_TARGET",
        target_name="Course Deficit",
        outcome_definition="Final score < 50%",
        positive_label_definition="Scores < 50%",
        negative_label_definition="Scores >= 50%",
        passing_threshold_percentage=50.0,
        status="ACTIVE",
    )
    session.add(target)
    session.commit()

    res = client.post(
        "/api/v1/risk/predictions/generate",
        json={"subject_id": str(SUBJECT_A_ID), "target_id": str(target.id), "target_student_id": str(stud_c_profile_id)},
    )
    assert res.status_code == 200
    preds = res.json()
    assert len(preds) == 1
    pred = preds[0]
    assert pred["risk_classification"] in (RiskClassification.HIGH.value, RiskClassification.MODERATE.value)
    assert pred["risk_score"] is not None
    assert len(pred["explanations"]) >= 1

    exp_texts = [e["explanation_text"] for e in pred["explanations"]]
    assert any("continuous assessment" in t.lower() for t in exp_texts)
    assert any(e["is_adverse_factor"] for e in pred["explanations"])
    session.close()


def test_student_role_access_guard_and_isolation():
    """
    Verifies that students can only inspect their own risk profile, cannot view peers,
    cannot trigger model training or prediction generation, and placement officers are barred.
    """
    # 1. Student A queries self profile -> Permitted (200)
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(STUDENT_A_USER_ID, UserRole.STUDENT)
    client = TestClient(app)
    res_self = client.get(f"/api/v1/risk/students/{STUDENT_A_PROFILE_ID}/subjects/{SUBJECT_A_ID}/profile")
    assert res_self.status_code == 200
    assert res_self.json()["student_id"] == str(STUDENT_A_PROFILE_ID)

    # 2. Student A attempts to query Student B's profile -> Forbidden (403)
    res_peer = client.get(f"/api/v1/risk/students/{STUDENT_B_PROFILE_ID}/subjects/{SUBJECT_A_ID}/profile")
    assert res_peer.status_code == 403

    # 3. Student A attempts to view cohort summary -> Forbidden (403)
    res_cohort = client.get(f"/api/v1/risk/cohort/subjects/{SUBJECT_A_ID}/summary")
    assert res_cohort.status_code == 403

    # 4. Student A attempts to trigger prediction generation -> Forbidden (403)
    res_gen = client.post(
        "/api/v1/risk/predictions/generate",
        json={"subject_id": str(SUBJECT_A_ID), "target_id": str(uuid.uuid4())},
    )
    assert res_gen.status_code == 403

    # 5. Placement Officer attempts to access student risk -> Forbidden (403)
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(PLACEMENT_USER_ID, UserRole.PLACEMENT_OFFICER)
    res_placement = client.get(f"/api/v1/risk/students/{STUDENT_A_PROFILE_ID}/subjects/{SUBJECT_A_ID}/profile")
    assert res_placement.status_code == 403


def test_cohort_risk_summary():
    """
    Verifies cohort risk summary aggregation across all enrolled students in a subject.
    """
    app.dependency_overrides[get_current_active_user] = lambda: make_current_user(FACULTY_A_ID, UserRole.FACULTY)
    client = TestClient(app)

    res = client.get(f"/api/v1/risk/cohort/subjects/{SUBJECT_A_ID}/summary")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["subject_code"] == "CS401"
    assert data["total_enrolled"] >= 2
    assert len(data["students"]) >= 2
    assert "scientific_disclaimer" in data
