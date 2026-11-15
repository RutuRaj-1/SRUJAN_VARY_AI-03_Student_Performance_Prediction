import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.enums import (
    UserRole,
    AccountStatus,
    AssessmentType,
    QuestionType,
    QuestionDifficulty,
    AttemptStatus,
    ResponseEvaluationStatus,
    EvidenceEligibilityStatus,
    EvidenceSufficiencyLevel,
    ConfidenceCategory,
    MasteryStatus,
    AttainmentStatus,
    LearningGapType,
)
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.syllabus import AcademicProgram, AcademicSubject, SyllabusDocument, SyllabusUnit, SyllabusTopic, LearningOutcome
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
)
from app.models.assessment import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentQuestionMapping,
    AssessmentAttempt,
    AssessmentResponse,
)
from app.models.mastery import (
    MasteryAnalysisJob,
    MasteryEvidenceRecord,
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)

# In-memory test SQLite DB
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
PROGRAM_A_ID = uuid.uuid4()
SUBJECT_A_ID = uuid.uuid4()
UNIT_1_ID = uuid.uuid4()
TOPIC_1_ID = uuid.uuid4()  # Binary Search Trees (Assessed)
TOPIC_2_ID = uuid.uuid4()  # Graph Traversal (Unassessed -> Insufficient Evidence)
OUTCOME_1_ID = uuid.uuid4()
OUTCOME_2_ID = uuid.uuid4()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Institutions
    inst_a = Institution(id=INST_A_ID, name="Apex Institute of Technology", institution_code="AIT", city="Pune", state="Maharashtra")
    inst_b = Institution(id=INST_B_ID, name="Metropolitan Tech", institution_code="MTECH", city="Mumbai", state="Maharashtra")
    session.add_all([inst_a, inst_b])

    # Faculty & Students
    fac = Profile(id=FACULTY_A_ID, full_name="Prof. Donald Knuth", email="knuth@ait.edu", role=UserRole.FACULTY.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_a = Profile(id=STUDENT_A_USER_ID, full_name="Ada Lovelace", email="ada@ait.edu", role=UserRole.STUDENT.value, institution_id=INST_A_ID, account_status=AccountStatus.ACTIVE.value)
    stud_user_b = Profile(id=STUDENT_B_USER_ID, full_name="Charles Babbage", email="charles@mtech.edu", role=UserRole.STUDENT.value, institution_id=INST_B_ID, account_status=AccountStatus.ACTIVE.value)
    session.add_all([fac, stud_user_a, stud_user_b])

    # Program & Subject
    prog = AcademicProgram(id=PROGRAM_A_ID, institution_id=INST_A_ID, name="B.Tech CS", code="BTECH-CS", duration_years=4)
    subj = AcademicSubject(id=SUBJECT_A_ID, institution_id=INST_A_ID, program_id=PROGRAM_A_ID, name="Data Structures", code="CS201", semester=4, academic_year="2024-2025")
    session.add_all([prog, subj])

    # Syllabus Document
    doc = SyllabusDocument(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        uploaded_by=FACULTY_A_ID,
        file_name="cs201_syllabus.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        storage_path="/uploads/cs201_syllabus.pdf",
        status="APPROVED",
    )
    session.add(doc)

    # Syllabus Unit & Topics
    unit1 = SyllabusUnit(id=UNIT_1_ID, document_id=doc.id, subject_id=SUBJECT_A_ID, unit_number=1, title="Trees and Graphs", estimated_hours=12)
    topic1 = SyllabusTopic(id=TOPIC_1_ID, unit_id=UNIT_1_ID, topic_name="Binary Search Trees", order_index=1)
    topic2 = SyllabusTopic(id=TOPIC_2_ID, unit_id=UNIT_1_ID, topic_name="Graph Traversal (BFS & DFS)", order_index=2)
    session.add_all([unit1, topic1, topic2])

    # Learning Outcomes
    lo1 = LearningOutcome(id=OUTCOME_1_ID, subject_id=SUBJECT_A_ID, unit_id=UNIT_1_ID, outcome_code="CO1", description="Implement and rebalance search trees", bloom_level="APPLY")
    lo2 = LearningOutcome(id=OUTCOME_2_ID, subject_id=SUBJECT_A_ID, unit_id=UNIT_1_ID, outcome_code="CO2", description="Analyze graph traversal complexity", bloom_level="ANALYZE")
    session.add_all([lo1, lo2])

    # Student Academic Profiles
    stud_a = StudentAcademicProfile(id=STUDENT_A_PROFILE_ID, institution_id=INST_A_ID, profile_id=STUDENT_A_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2024-CSE-001", first_name="Ada", last_name="Lovelace", department="CSE", admission_year=2024, current_semester=4)
    stud_b = StudentAcademicProfile(id=STUDENT_B_PROFILE_ID, institution_id=INST_B_ID, profile_id=STUDENT_B_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2024-MTECH-001", first_name="Charles", last_name="Babbage", department="CSE", admission_year=2024, current_semester=4)
    session.add_all([stud_a, stud_b])

    # Enrollments
    enr_a = StudentSubjectEnrollment(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_A_ID, academic_year="2024-2025", semester=4, enrollment_status="ACTIVE")
    session.add(enr_a)

    # Online Assessment with 2 questions mapped to Topic 1
    asmt = AcademicAssessment(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        assessment_name="Mid-Term Test",
        assessment_type="INTERNAL_TEST",
        academic_year="2024-2025",
        semester=4,
        maximum_marks=20.0,
        passing_marks=8.0,
        status="PUBLISHED",
    )
    session.add(asmt)

    q1 = AssessmentQuestion(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        topic_id=TOPIC_1_ID,
        learning_outcome_id=OUTCOME_1_ID,
        question_text="What is search time complexity in AVL tree?",
        question_type=QuestionType.MCQ.value,
        difficulty=QuestionDifficulty.MEDIUM.value,
        bloom_level="ANALYZE",
        default_marks=10.0,
    )
    q2 = AssessmentQuestion(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        subject_id=SUBJECT_A_ID,
        topic_id=TOPIC_1_ID,
        learning_outcome_id=OUTCOME_1_ID,
        question_text="Explain tree rotation balance factor.",
        question_type=QuestionType.LONG_ANSWER.value,
        difficulty=QuestionDifficulty.HARD.value,
        bloom_level="APPLY",
        default_marks=10.0,
    )
    session.add_all([q1, q2])

    map1 = AssessmentQuestionMapping(assessment_id=asmt.id, question_id=q1.id, display_order=1, marks_allocated=10.0, required=True)
    map2 = AssessmentQuestionMapping(assessment_id=asmt.id, question_id=q2.id, display_order=2, marks_allocated=10.0, required=True)
    session.add_all([map1, map2])

    # Attempt 1 for Student A: Completed & Evaluated (Ada scored 9/10 on Q1, 8/10 on Q2 = 17/20 => 85%)
    now = datetime.now(timezone.utc)
    att1 = AssessmentAttempt(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        assessment_id=asmt.id,
        student_id=STUDENT_A_PROFILE_ID,
        attempt_number=1,
        attempt_status=AttemptStatus.EVALUATED.value,
        started_at=now - timedelta(days=2),
        submitted_at=now - timedelta(days=2) + timedelta(minutes=40),
        total_marks=20.0,
        marks_obtained=17.0,
        evaluation_status="EVALUATED",
    )
    session.add(att1)

    resp1 = AssessmentResponse(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        attempt_id=att1.id,
        question_id=q1.id,
        response_payload={"answer": "O(log n)"},
        marks_awarded=9.0,
        evaluation_status=ResponseEvaluationStatus.AUTO_EVALUATED.value,
        is_auto_evaluated=True,
        saved_at=now - timedelta(days=2),
    )
    resp2 = AssessmentResponse(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        attempt_id=att1.id,
        question_id=q2.id,
        response_payload={"answer": "Balance factor = height(left) - height(right)"},
        marks_awarded=8.0,
        evaluation_status=ResponseEvaluationStatus.FACULTY_VERIFIED.value,
        is_auto_evaluated=False,
        saved_at=now - timedelta(days=2),
    )
    session.add_all([resp1, resp2])

    # Also add an Official Gradebook record for this same assessment (To verify Anti-Double-Counting!)
    gradebook_rec = StudentAssessmentRecord(
        id=uuid.uuid4(),
        institution_id=INST_A_ID,
        student_id=STUDENT_A_PROFILE_ID,
        assessment_id=asmt.id,
        marks_obtained=17.0,
        maximum_marks_snapshot=20.0,
        result_status="PASSED",
        verification_status="VERIFIED",
    )
    session.add(gradebook_rec)

    session.commit()
    session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


current_test_user = CurrentUser(
    user_id=str(FACULTY_A_ID),
    email="knuth@ait.edu",
    role=UserRole.FACULTY,
    account_status=AccountStatus.ACTIVE,
    full_name="Prof. Donald Knuth",
    institution_id=str(INST_A_ID),
    raw_claims={},
)


def mock_get_current_user():
    return current_test_user


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


# =========================================================================
# TEST SUITE
# =========================================================================

def test_mastery_analysis_job_trigger_and_anti_double_counting():
    """Verify analysis job runs, calculates topic mastery, and avoids double-counting gradebook copy."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    resp = client.post(
        "/api/v1/mastery/analyze",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "student_id": str(STUDENT_A_PROFILE_ID),
            "academic_year": "2024-2025",
            "semester": 4,
            "calculation_version": "v1.0-deterministic",
            "include_practice_tests": False,
        },
    )
    assert resp.status_code == 201
    job_data = resp.json()
    assert job_data["status"] == "COMPLETED"
    assert job_data["eligible_evidence_count"] == 2
    # The duplicate gradebook record was cleanly EXCLUDED!
    assert job_data["excluded_evidence_count"] >= 1


def test_student_mastery_profile_and_insufficient_evidence_preservation():
    """Verify Topic 1 shows 85% Mastered, and unassessed Topic 2 shows INSUFFICIENT_EVIDENCE (not 0%)."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    resp = client.get(f"/api/v1/mastery/students/{STUDENT_A_PROFILE_ID}?subject_id={SUBJECT_A_ID}")
    assert resp.status_code == 200
    prof = resp.json()
    assert prof["student_name"] == "Ada Lovelace"
    assert prof["total_topics_analyzed"] == 2

    # Topic 1: Binary Search Trees (Assessed: 17 / 20 = 85.0%)
    t1 = [t for t in prof["topic_results"] if t["topic_name"] == "Binary Search Trees"][0]
    assert t1["eligible_question_count"] == 2
    assert t1["mastery_percentage"] == 85.0
    assert t1["mastery_status"] == MasteryStatus.MASTERED.value
    assert t1["evidence_sufficiency"] in [EvidenceSufficiencyLevel.MODERATE.value, EvidenceSufficiencyLevel.STRONG.value]

    # Topic 2: Graph Traversal (Unassessed: MUST BE NULL, NEVER 0.0%)
    t2 = [t for t in prof["topic_results"] if t["topic_name"] == "Graph Traversal (BFS & DFS)"][0]
    assert t2["eligible_question_count"] == 0
    assert t2["mastery_percentage"] is None, "CRITICAL ERROR: Unassessed topic defaulted to 0%!"
    assert t2["mastery_status"] == MasteryStatus.INSUFFICIENT_EVIDENCE.value
    assert t2["evidence_sufficiency"] == EvidenceSufficiencyLevel.INSUFFICIENT.value

    # Outcome 1: CO1 (Assessed: 17/20 = 85%)
    co1 = [o for o in prof["outcome_results"] if o["outcome_code"] == "CO1"][0]
    assert co1["attainment_percentage"] == 85.0
    assert co1["attainment_status"] == AttainmentStatus.ATTAINED.value

    # Outcome 2: CO2 (Unassessed: MUST BE NULL)
    co2 = [o for o in prof["outcome_results"] if o["outcome_code"] == "CO2"][0]
    assert co2["attainment_percentage"] is None


def test_learning_gap_discovery_distinguishes_low_performance_from_unassessed():
    """Verify that unassessed topics generate INSUFFICIENT_EVIDENCE gaps, not performance failure."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    resp = client.get(f"/api/v1/mastery/students/{STUDENT_A_PROFILE_ID}/gaps?subject_id={SUBJECT_A_ID}")
    assert resp.status_code == 200
    gaps = resp.json()
    assert len(gaps) >= 1

    # Unassessed topic gap is explicitly typed as INSUFFICIENT_EVIDENCE with INFO severity
    unassessed_gap = [g for g in gaps if g["topic_name"] == "Graph Traversal (BFS & DFS)"][0]
    assert unassessed_gap["finding_type"] == LearningGapType.INSUFFICIENT_EVIDENCE.value
    assert unassessed_gap["severity"] == "INFO"


def test_evidence_traceability_and_exclusion_inspection():
    """Verify that every result traces back to questions, and excluded evidence shows justification."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    prof = client.get(f"/api/v1/mastery/students/{STUDENT_A_PROFILE_ID}?subject_id={SUBJECT_A_ID}").json()
    t1_result_id = [t for t in prof["topic_results"] if t["topic_name"] == "Binary Search Trees"][0]["id"]

    # 1. Eligible evidence inspection
    ev_resp = client.get(f"/api/v1/mastery/results/{t1_result_id}/evidence")
    assert ev_resp.status_code == 200
    evidence_items = ev_resp.json()
    assert len(evidence_items) == 2
    assert all(e["eligibility_status"] == "ELIGIBLE" for e in evidence_items)

    # 2. Excluded evidence inspection (Verifying duplicate gradebook rejection)
    ex_resp = client.get(f"/api/v1/mastery/results/{t1_result_id}/excluded-evidence")
    assert ex_resp.status_code == 200
    excluded_items = ex_resp.json()
    assert len(excluded_items) >= 1
    dup_gradebook = [e for e in excluded_items if e["exclusion_reason"] == "DUPLICATE_GRADEBOOK_RECORD"][0]
    assert dup_gradebook["source_entity_type"] == "OFFICIAL_GRADEBOOK_RECORD"


def test_longitudinal_performance_trends():
    """Verify performance trend points preserve timestamps and compute observations."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    resp = client.get(f"/api/v1/mastery/students/{STUDENT_A_PROFILE_ID}/trends?subject_id={SUBJECT_A_ID}")
    assert resp.status_code == 200
    trends = resp.json()
    assert trends["observation_count"] == 2
    assert len(trends["timeline"]) == 2
    assert "DISCLAIMER" in trends["scientific_disclaimer"]


def test_cohort_mastery_summary():
    """Verify faculty subject-level cohort summary and coverage percentage."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    resp = client.get(f"/api/v1/mastery/cohort/{SUBJECT_A_ID}/summary")
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["subject_code"] == "CS201"
    assert summary["students_analyzed"] >= 1
    assert summary["curriculum_coverage_percentage"] == 50.0  # 1 out of 2 topics covered


def test_student_role_access_guard_and_isolation():
    """Verify student can view their own profile but is forbidden from viewing other students."""
    global current_test_user
    # Switch to Student A
    current_test_user = CurrentUser(
        user_id=str(STUDENT_A_USER_ID),
        email="ada@ait.edu",
        role=UserRole.STUDENT,
        account_status=AccountStatus.ACTIVE,
        full_name="Ada Lovelace",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )

    # 1. Student A viewing own profile -> Allowed
    own_resp = client.get(f"/api/v1/mastery/students/{STUDENT_A_PROFILE_ID}?subject_id={SUBJECT_A_ID}")
    assert own_resp.status_code == 200

    # 2. Student A attempting to trigger an analysis job -> Forbidden (Requires Faculty/Admin)
    job_resp = client.post(
        "/api/v1/mastery/analyze",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "student_id": str(STUDENT_A_PROFILE_ID),
        },
    )
    assert job_resp.status_code == 403

    # 3. Student A attempting to view Student B's profile -> Forbidden
    other_resp = client.get(f"/api/v1/mastery/students/{STUDENT_B_PROFILE_ID}?subject_id={SUBJECT_A_ID}")
    assert other_resp.status_code == 403
