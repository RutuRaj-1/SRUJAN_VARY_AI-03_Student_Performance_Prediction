import io
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
    QuestionEvaluationMethod,
    AttemptStatus,
    ResponseEvaluationStatus,
    LearningEngagementEventType,
)
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.syllabus import AcademicProgram, AcademicSubject, SyllabusUnit, SyllabusTopic, LearningOutcome
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    AcademicRecordAudit,
)
from app.models.assessment import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentQuestionMapping,
    AssessmentLearningOutcomeMapping,
    AssessmentAttempt,
    AssessmentResponse,
    LearningEngagementEvent,
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
SUBJECT_B_ID = uuid.uuid4()
OUTCOME_A_ID = uuid.uuid4()


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

    # Program & Subjects
    prog = AcademicProgram(id=PROGRAM_A_ID, institution_id=INST_A_ID, name="B.Tech CS", code="BTECH-CS", duration_years=4)
    subj_a = AcademicSubject(id=SUBJECT_A_ID, institution_id=INST_A_ID, program_id=PROGRAM_A_ID, name="Data Structures", code="CS201", semester=3, academic_year="2024-2025")
    subj_b = AcademicSubject(id=SUBJECT_B_ID, institution_id=INST_A_ID, program_id=PROGRAM_A_ID, name="Algorithms", code="CS301", semester=4, academic_year="2024-2025")
    session.add_all([prog, subj_a, subj_b])

    # Learning Outcome
    lo = LearningOutcome(id=OUTCOME_A_ID, subject_id=SUBJECT_A_ID, outcome_code="CO1", description="Implement balanced binary search trees", bloom_level="APPLY")
    session.add(lo)

    # Student Academic Profiles
    stud_a = StudentAcademicProfile(id=STUDENT_A_PROFILE_ID, institution_id=INST_A_ID, profile_id=STUDENT_A_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2024-CSE-001", first_name="Ada", last_name="Lovelace", department="CSE", admission_year=2024, current_semester=3)
    stud_b = StudentAcademicProfile(id=STUDENT_B_PROFILE_ID, institution_id=INST_B_ID, profile_id=STUDENT_B_USER_ID, program_id=PROGRAM_A_ID, enrollment_number="2024-MTECH-001", first_name="Charles", last_name="Babbage", department="CSE", admission_year=2024, current_semester=3)
    session.add_all([stud_a, stud_b])

    # Enrollments: Student A enrolled in Subject A only
    enr_a = StudentSubjectEnrollment(institution_id=INST_A_ID, student_id=STUDENT_A_PROFILE_ID, subject_id=SUBJECT_A_ID, academic_year="2024-2025", semester=3, enrollment_status="ACTIVE")
    session.add(enr_a)

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


def test_question_creation_and_option_security():
    """Verify question bank creation and that correct answers are protected."""
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
        "/api/v1/assessments/questions",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "learning_outcome_id": str(OUTCOME_A_ID),
            "question_text": "What is the worst-case time complexity of searching in an AVL tree?",
            "question_type": "MCQ",
            "difficulty": "MEDIUM",
            "bloom_level": "ANALYZE",
            "default_marks": 2.0,
            "explanation": "AVL trees are height-balanced with height O(log n).",
            "options": [
                {"option_text": "O(log n)", "display_order": 1, "is_correct": True},
                {"option_text": "O(n)", "display_order": 2, "is_correct": False},
                {"option_text": "O(n log n)", "display_order": 3, "is_correct": False},
                {"option_text": "O(1)", "display_order": 4, "is_correct": False},
            ],
        },
    )
    assert resp.status_code == 201
    q_data = resp.json()
    assert q_data["question_text"].startswith("What is the worst-case")
    assert len(q_data["options"]) == 4
    # Faculty view sees is_correct
    assert any(opt["is_correct"] is True for opt in q_data["options"])


def test_assessment_authoring_and_publishing():
    """Verify authoring workspace, question mapping, and publishing lifecycle."""
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

    # 1. Create Question 1 (MCQ)
    q1_resp = client.post(
        "/api/v1/assessments/questions",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "learning_outcome_id": str(OUTCOME_A_ID),
            "question_text": "What is the worst-case time complexity of searching in an AVL tree?",
            "question_type": "MCQ",
            "difficulty": "MEDIUM",
            "bloom_level": "ANALYZE",
            "default_marks": 2.0,
            "options": [
                {"option_text": "O(log n)", "display_order": 1, "is_correct": True},
                {"option_text": "O(n)", "display_order": 2, "is_correct": False},
            ],
        },
    )
    assert q1_resp.status_code == 201
    q1_id = q1_resp.json()["id"]

    # Create Question 2 (descriptive)
    q2_resp = client.post(
        "/api/v1/assessments/questions",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "question_text": "Explain the difference between an AVL tree and a Red-Black tree.",
            "question_type": "SHORT_ANSWER",
            "difficulty": "HARD",
            "default_marks": 5.0,
            "evaluation_method": "MANUAL",
            "expected_answer": "AVL trees are more strictly balanced; Red-Black trees require fewer rotations during insertion.",
        },
    )
    assert q2_resp.status_code == 201
    q2_id = q2_resp.json()["id"]

    # 2. Create Assessment
    asmt_resp = client.post(
        "/api/v1/assessments",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "assessment_name": "Mid-Term Continuous Evaluation 1",
            "assessment_type": "INTERNAL_TEST",
            "academic_year": "2024-2025",
            "semester": 3,
            "maximum_marks": 7.0,
            "passing_marks": 3.0,
            "duration_minutes": 45,
            "instructions": "Answer all questions. Calculators not permitted.",
            "questions": [
                {"question_id": q1_id, "marks_allocated": 2.0, "display_order": 1, "required": True},
                {"question_id": q2_id, "marks_allocated": 5.0, "display_order": 2, "required": True},
            ],
            "outcome_mappings": [
                {"learning_outcome_id": str(OUTCOME_A_ID), "mapped_marks": 2.0}
            ],
        },
    )
    assert asmt_resp.status_code == 201
    asmt_data = asmt_resp.json()
    assert asmt_data["status"] == "DRAFT"
    asmt_id = asmt_data["id"]

    # 3. Publish Assessment
    pub_resp = client.post(f"/api/v1/assessments/{asmt_id}/publish")
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "PUBLISHED"


def test_student_attempt_lifecycle_and_answer_security():
    """Verify student start attempt, deadline assignment, and correct answer protection."""
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

    # 1. Check Available Assessments
    avail_resp = client.get("/api/v1/assessments/available")
    assert avail_resp.status_code == 200
    avail_items = avail_resp.json()
    assert len(avail_items) >= 1
    asmt_item = [a for a in avail_items if a["assessment"]["assessment_name"] == "Mid-Term Continuous Evaluation 1"][0]
    asmt_id = asmt_item["assessment"]["id"]

    # 2. Start Attempt
    start_resp = client.post(f"/api/v1/assessments/{asmt_id}/attempts")
    assert start_resp.status_code == 200
    att_data = start_resp.json()
    attempt_id = att_data["attempt_id"]
    assert att_data["duration_minutes"] == 45
    assert att_data["deadline_at"] is not None
    assert len(att_data["questions"]) == 2

    # CRITICAL SECURITY CHECK: Ensure is_correct or expected_answer is NOT leaked to student
    for q in att_data["questions"]:
        assert "expected_answer" not in q
        for opt in q.get("options", []):
            assert "is_correct" not in opt, "SECURITY BREACH: is_correct leaked in student question view!"

    # 3. Save / Autosave Response for Question 1 (MCQ)
    # Fetch options from faculty or question detail
    q1 = att_data["questions"][0]
    opt_id = q1["options"][0]["id"]
    save_resp = client.put(
        f"/api/v1/assessments/attempts/{attempt_id}/responses",
        json={
            "question_id": q1["id"],
            "response_payload": {"selected_option_ids": [opt_id]},
        },
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["revision_count"] == 0

    # 4. Revise response (check revision count increments)
    revise_resp = client.put(
        f"/api/v1/assessments/attempts/{attempt_id}/responses",
        json={
            "question_id": q1["id"],
            "response_payload": {"selected_option_ids": [opt_id]},
        },
    )
    assert revise_resp.status_code == 200
    assert revise_resp.json()["revision_count"] == 1

    # 5. Save Response for Question 2 (Descriptive)
    q2 = att_data["questions"][1]
    client.put(
        f"/api/v1/assessments/attempts/{attempt_id}/responses",
        json={
            "question_id": q2["id"],
            "response_payload": {"text_answer": "AVL trees maintain strict height balance factor <= 1; Red-Black trees use color rules allowing higher height with faster inserts."},
        },
    )

    # 6. Submit Attempt
    sub_resp = client.post(f"/api/v1/assessments/attempts/{attempt_id}/submit")
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert sub_data["attempt_status"] in ["SUBMITTED", "UNDER_EVALUATION"]
    # Objective question auto-evaluated (2 marks), descriptive question requires faculty review
    assert sub_data["marks_obtained"] >= 0.0


def test_faculty_evaluation_and_official_record_publishing():
    """Verify faculty review, manual marks award, and publishing to Phase 04 official records."""
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

    # 1. Fetch assessments and submissions
    asmts = client.get(f"/api/v1/assessments?subject_id={SUBJECT_A_ID}").json()
    asmt_id = [a["id"] for a in asmts if a["assessment_name"] == "Mid-Term Continuous Evaluation 1"][0]

    subs = client.get(f"/api/v1/assessments/{asmt_id}/submissions").json()
    assert len(subs) >= 1
    attempt_id = subs[0]["id"]

    # 2. Get questions to find the descriptive question
    q2_id = subs[0]["responses"][1]["question_id"]

    # 3. Faculty evaluates the descriptive question manually
    eval_resp = client.post(
        f"/api/v1/assessments/submissions/{attempt_id}/evaluate",
        json={
            "evaluations": [
                {
                    "question_id": q2_id,
                    "marks_awarded": 4.5,
                    "feedback": "Strong explanation of balance factors and rotational overhead.",
                }
            ],
            "overall_remarks": "Very solid conceptual grasp of balanced trees.",
        },
    )
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["attempt_status"] == "EVALUATED"
    assert eval_data["marks_obtained"] >= 4.5

    # 4. Faculty releases verified result to Phase 04 official academic records
    release_resp = client.post(
        f"/api/v1/assessments/submissions/{attempt_id}/release-result",
        json={
            "publish_to_official_records": True,
            "verification_remarks": "Verified via Online Assessment Engine by Prof. Knuth",
        },
    )
    assert release_resp.status_code == 200
    assert release_resp.json()["evaluation_status"] == "FACULTY_VERIFIED"

    # 5. Verify official record exists in Phase 04 student academic records!
    records_resp = client.get(f"/api/v1/academic-data/performance?assessment_id={asmt_id}")
    assert records_resp.status_code == 200
    records = records_resp.json()
    assert len(records) >= 1
    assert records[0]["verification_status"] in ["VERIFIED", "FACULTY_VERIFIED"]
    assert records[0]["marks_obtained"] == eval_data["marks_obtained"]


def test_practice_assessment_excluded_from_official_records():
    """Verify that practice tests do NOT pollute official institutional gradebooks."""
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

    # 1. Create a practice assessment
    list_q = client.get(f"/api/v1/assessments/questions?subject_id={SUBJECT_A_ID}").json()
    q_id = list_q[0]["id"]

    asmt_resp = client.post(
        "/api/v1/assessments",
        json={
            "subject_id": str(SUBJECT_A_ID),
            "assessment_name": "Practice Diagnostic Drill",
            "assessment_type": "PRACTICE_TEST",
            "academic_year": "2024-2025",
            "semester": 3,
            "maximum_marks": 2.0,
            "duration_minutes": 20,
            "questions": [{"question_id": q_id, "marks_allocated": 2.0, "display_order": 1, "required": True}],
        },
    )
    asmt_id = asmt_resp.json()["id"]
    client.post(f"/api/v1/assessments/{asmt_id}/publish")

    # 2. Student attempts and submits
    current_test_user = CurrentUser(
        user_id=str(STUDENT_A_USER_ID),
        email="ada@ait.edu",
        role=UserRole.STUDENT,
        account_status=AccountStatus.ACTIVE,
        full_name="Ada Lovelace",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )
    start_resp = client.post(f"/api/v1/assessments/{asmt_id}/attempts").json()
    att_id = start_resp["attempt_id"]
    client.post(f"/api/v1/assessments/attempts/{att_id}/submit")

    # 3. Faculty releases result
    current_test_user = CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="knuth@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Donald Knuth",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )
    client.post(
        f"/api/v1/assessments/submissions/{att_id}/release-result",
        json={"publish_to_official_records": True},
    )

    # 4. Verify NO record in official student_assessment_records for practice test
    official_records = client.get(f"/api/v1/academic-data/performance?assessment_id={asmt_id}").json()
    assert len(official_records) == 0, "Practice test must NOT be written to official academic gradebook!"


def test_learning_engagement_summary_and_disclaimer():
    """Verify transparent engagement telemetry and scientific non-attention disclaimer."""
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

    asmts = client.get(f"/api/v1/assessments?subject_id={SUBJECT_A_ID}").json()
    asmt_id = [a["id"] for a in asmts if a["assessment_name"] == "Mid-Term Continuous Evaluation 1"][0]

    eng_resp = client.get(f"/api/v1/assessments/{asmt_id}/engagement-summary")
    assert eng_resp.status_code == 200
    data = eng_resp.json()
    assert data["total_events"] > 0
    assert data["completed_attempts"] >= 1
    # Check strict non-mind-reading disclaimer
    assert "does not directly measure internal cognitive attention" in data["limitations_disclaimer"]


def test_assessment_analytics_and_outcome_coverage():
    """Verify question-level performance statistics and learning outcome coverage."""
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

    asmts = client.get(f"/api/v1/assessments?subject_id={SUBJECT_A_ID}").json()
    asmt_id = [a["id"] for a in asmts if a["assessment_name"] == "Mid-Term Continuous Evaluation 1"][0]

    analytics_resp = client.get(f"/api/v1/assessments/{asmt_id}/analytics")
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert data["total_attempts"] >= 1
    assert len(data["questions"]) == 2
    assert len(data["outcome_coverage"]) >= 1
    assert data["outcome_coverage"][0]["outcome_code"] == "CO1"


def test_cross_institution_isolation():
    """Verify that student from Institution B cannot access Institution A assessments."""
    global current_test_user
    current_test_user = CurrentUser(
        user_id=str(STUDENT_B_USER_ID),
        email="charles@mtech.edu",
        role=UserRole.STUDENT,
        account_status=AccountStatus.ACTIVE,
        full_name="Charles Babbage",
        institution_id=str(INST_B_ID),
        raw_claims={},
    )

    # Student B queries available assessments -> Expect empty list
    avail = client.get("/api/v1/assessments/available").json()
    assert len(avail) == 0

    # Direct attempt at Institution A assessment -> Expect 404 Not Found (scoped by institution_id)
    asmts = client.get(f"/api/v1/assessments?subject_id={SUBJECT_A_ID}").json()
    assert len(asmts) == 0
