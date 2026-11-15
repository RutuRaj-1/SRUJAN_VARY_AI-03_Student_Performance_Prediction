import io
import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import openpyxl

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.enums import (
    UserRole,
    AccountStatus,
    AssessmentType,
    AssessmentResultStatus,
    AttendanceStatus,
    RecordVerificationStatus,
    ImportCategory,
)
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.syllabus import AcademicProgram, AcademicSubject
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
    AcademicImportJob,
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
STUDENT_A_ID = uuid.uuid4()
PROGRAM_A_ID = uuid.uuid4()
SUBJECT_A_ID = uuid.uuid4()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Institutions
    inst_a = Institution(
        id=INST_A_ID,
        name="Apex Institute of Technology",
        institution_code="AIT-ACAD",
        institution_type="COLLEGE",
        city="Bengaluru",
        state="Karnataka",
    )
    inst_b = Institution(
        id=INST_B_ID,
        name="Zenith University",
        institution_code="ZU-ACAD",
        institution_type="UNIVERSITY",
        city="Hyderabad",
        state="Telangana",
    )
    session.add_all([inst_a, inst_b])

    # Profiles
    fac = Profile(
        id=FACULTY_A_ID,
        full_name="Prof. David Patterson",
        email="patterson@ait.edu",
        role=UserRole.FACULTY.value,
        institution_id=INST_A_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    stud = Profile(
        id=STUDENT_A_ID,
        full_name="Grace Hopper",
        email="grace.hopper@ait.edu",
        role=UserRole.STUDENT.value,
        institution_id=INST_A_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    session.add_all([fac, stud])

    # Program & Subject
    prog = AcademicProgram(
        id=PROGRAM_A_ID,
        institution_id=INST_A_ID,
        name="B.Tech Computer Science",
        code="BTECH-CSE",
        degree_type="Bachelor of Technology",
        duration_years=4,
    )
    subj = AcademicSubject(
        id=SUBJECT_A_ID,
        institution_id=INST_A_ID,
        program_id=PROGRAM_A_ID,
        name="Computer Architecture",
        code="CS302",
        semester=4,
        academic_year="2024-2025",
        credits=4,
        total_hours=45,
    )
    session.add_all([prog, subj])
    session.commit()
    session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def mock_faculty_user():
    return CurrentUser(
        user_id=str(FACULTY_A_ID),
        email="patterson@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. David Patterson",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )


def mock_student_user():
    return CurrentUser(
        user_id=str(STUDENT_A_ID),
        email="grace.hopper@ait.edu",
        role=UserRole.STUDENT,
        account_status=AccountStatus.ACTIVE,
        full_name="Grace Hopper",
        institution_id=str(INST_A_ID),
        raw_claims={},
    )


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_faculty_user
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


def test_create_student_profile_and_unique_constraint():
    resp = client.post(
        "/api/v1/academic-data/students",
        json={
            "enrollment_number": "2022-CSE-001",
            "admission_number": "ADM-001",
            "first_name": "Alan",
            "last_name": "Turing",
            "email": "alan.turing@ait.edu",
            "department": "Computer Science",
            "admission_year": 2022,
            "current_semester": 4,
            "academic_status": "ENROLLED",
            "institution_id": str(INST_A_ID),
            "program_id": str(PROGRAM_A_ID),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["enrollment_number"] == "2022-CSE-001"

    # Attempt duplicate in same institution -> Expect 409 Conflict
    dup_resp = client.post(
        "/api/v1/academic-data/students",
        json={
            "enrollment_number": "2022-CSE-001",
            "first_name": "Duplicate",
            "last_name": "Student",
            "department": "Computer Science",
            "admission_year": 2022,
            "current_semester": 4,
            "institution_id": str(INST_A_ID),
            "program_id": str(PROGRAM_A_ID),
        },
    )
    assert dup_resp.status_code == 409


def test_enrollment_and_duplicate_prevention():
    # Fetch created student
    studs_resp = client.get("/api/v1/academic-data/students")
    assert studs_resp.status_code == 200
    students = studs_resp.json()
    assert len(students) > 0
    student_id = students[0]["id"]

    enroll_resp = client.post(
        "/api/v1/academic-data/enrollments",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "subject_id": str(SUBJECT_A_ID),
            "academic_year": "2024-2025",
            "semester": 4,
            "enrollment_status": "ACTIVE",
        },
    )
    assert enroll_resp.status_code == 201
    data = enroll_resp.json()
    assert data["enrollment_status"] == "ACTIVE"

    # Duplicate enrollment in same term -> Expect 409 Conflict
    dup_enroll = client.post(
        "/api/v1/academic-data/enrollments",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "subject_id": str(SUBJECT_A_ID),
            "academic_year": "2024-2025",
            "semester": 4,
            "enrollment_status": "ACTIVE",
        },
    )
    assert dup_enroll.status_code == 409


def test_assessment_creation_and_marks_validation():
    # 1. Create Assessment (Max marks = 50.0)
    asmt_resp = client.post(
        "/api/v1/academic-data/assessments",
        json={
            "institution_id": str(INST_A_ID),
            "subject_id": str(SUBJECT_A_ID),
            "academic_year": "2024-2025",
            "semester": 4,
            "assessment_name": "Mid-Term Exam",
            "assessment_type": "MID_TERM",
            "maximum_marks": 50.0,
            "passing_marks": 20.0,
            "weightage_percentage": 25.0,
        },
    )
    assert asmt_resp.status_code == 201
    asmt_id = asmt_resp.json()["id"]

    # Get student
    students = client.get("/api/v1/academic-data/students").json()
    student_id = students[0]["id"]

    # 2. Reject Negative Marks
    neg_resp = client.post(
        "/api/v1/academic-data/performance",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "assessment_id": asmt_id,
            "marks_obtained": -5.0,
            "result_status": "FAILED",
        },
    )
    assert neg_resp.status_code in [400, 422]

    # 3. Reject Marks Exceeding Maximum Marks
    exceed_resp = client.post(
        "/api/v1/academic-data/performance",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "assessment_id": asmt_id,
            "marks_obtained": 55.0,  # Max is 50.0
            "result_status": "PASSED",
        },
    )
    assert exceed_resp.status_code == 400
    assert "cannot exceed maximum marks" in exceed_resp.json()["detail"].lower()

    # 4. Valid Marks Record
    valid_resp = client.post(
        "/api/v1/academic-data/performance",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "assessment_id": asmt_id,
            "marks_obtained": 44.5,
            "result_status": "PASSED",
            "remarks": "Excellent analysis of pipelining hazards.",
        },
    )
    assert valid_resp.status_code in [200, 201]
    rec_data = valid_resp.json()
    assert rec_data["marks_obtained"] == 44.5
    assert rec_data["maximum_marks_snapshot"] == 50.0
    rec_id = rec_data["id"]

    # 5. Verify Record
    verify_resp = client.post(
        f"/api/v1/academic-data/records/{rec_id}/verify",
        json={"action": "VERIFY", "reason": "Verified against physical grade ledger."},
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verification_status"] == RecordVerificationStatus.VERIFIED.value

    # 6. Reject Overwrite on Verified Record
    overwrite_resp = client.post(
        "/api/v1/academic-data/performance",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "assessment_id": asmt_id,
            "marks_obtained": 48.0,
        },
    )
    assert overwrite_resp.status_code == 409
    assert "verified" in overwrite_resp.json()["detail"].lower()

    # 7. Audited Correction Workflow
    correct_resp = client.post(
        f"/api/v1/academic-data/records/{rec_id}/correction",
        json={"marks_obtained": 46.0, "reason": "Re-evaluation mark update authorized by exam controller."},
    )
    assert correct_resp.status_code == 200
    assert correct_resp.json()["marks_obtained"] == 46.0

    # 8. Check Audit Trail
    audits_resp = client.get(f"/api/v1/academic-data/audits?entity_id={rec_id}")
    assert audits_resp.status_code == 200
    audits = audits_resp.json()
    assert len(audits) >= 2  # VERIFY and CORRECTED
    actions = [a["action"] for a in audits]
    assert "VERIFY" in actions
    assert "CORRECTED" in actions


def test_attendance_recording():
    students = client.get("/api/v1/academic-data/students").json()
    student_id = students[0]["id"]

    att_resp = client.post(
        "/api/v1/academic-data/attendance",
        json={
            "institution_id": str(INST_A_ID),
            "student_id": student_id,
            "subject_id": str(SUBJECT_A_ID),
            "academic_year": "2024-2025",
            "semester": 4,
            "attendance_date": "2024-10-15T09:00:00Z",
            "session_name": "Lecture 08",
            "attendance_status": "PRESENT",
        },
    )
    assert att_resp.status_code == 201
    assert att_resp.json()["attendance_status"] == "PRESENT"


def test_import_csv_workflow_and_preview():
    csv_content = """enrollment_number,admission_number,first_name,last_name,email,department,admission_year,current_semester,program_code
2022-CSE-002,ADM-002,Bob,Smith,bob.smith@ait.edu,Computer Science,2022,4,BTECH-CSE
2022-CSE-003,ADM-003,Carol,Danvers,carol@ait.edu,Computer Science,2022,4,BTECH-CSE
2022-CSE-002,ADM-DUP,Duplicate,Student,dup@ait.edu,Computer Science,2022,4,BTECH-CSE
"""
    file_bytes = io.BytesIO(csv_content.encode("utf-8"))
    upload_resp = client.post(
        "/api/v1/academic-data/imports",
        files={"file": ("students_batch.csv", file_bytes, "text/csv")},
        data={"category": "STUDENTS", "institution_id": str(INST_A_ID)},
    )
    assert upload_resp.status_code == 201
    job_data = upload_resp.json()
    job_id = job_data["id"]
    assert job_data["total_rows"] == 3
    assert job_data["valid_rows"] == 2
    assert job_data["duplicate_rows"] == 1
    assert job_data["status"] == "PREVIEW_READY"
    assert len(job_data["preview_data"]) == 3

    # Check errors
    errs_resp = client.get(f"/api/v1/academic-data/imports/{job_id}/errors")
    assert errs_resp.status_code == 200
    errors = errs_resp.json()
    assert len(errors) == 1
    assert errors[0]["error_code"] == "DUPLICATE_IN_FILE"

    # Confirm execution
    confirm_resp = client.post(
        f"/api/v1/academic-data/imports/{job_id}/confirm",
        json={"allow_partial": True},
    )
    assert confirm_resp.status_code == 200
    res_data = confirm_resp.json()
    assert res_data["status"] == "COMPLETED"
    assert res_data["imported_rows"] == 2


def test_import_xlsx_workflow():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["enrollment_number", "admission_number", "first_name", "last_name", "email", "department", "admission_year", "current_semester", "program_code"])
    ws.append(["2022-CSE-010", "ADM-010", "David", "Miller", "david@ait.edu", "Computer Science", 2022, 4, "BTECH-CSE"])
    
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    upload_resp = client.post(
        "/api/v1/academic-data/imports",
        files={"file": ("students_batch.xlsx", file_stream, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"category": "STUDENTS", "institution_id": str(INST_A_ID)},
    )
    assert upload_resp.status_code == 201
    job = upload_resp.json()
    assert job["total_rows"] == 1
    assert job["valid_rows"] == 1


def test_data_quality_scan_and_overview():
    # 1. Run Data Quality Scan
    scan_resp = client.post("/api/v1/academic-data/quality/scan")
    assert scan_resp.status_code == 200
    findings = scan_resp.json()
    assert isinstance(findings, list)

    # 2. Get Overview Metrics
    overview_resp = client.get("/api/v1/academic-data/overview")
    assert overview_resp.status_code == 200
    stats = overview_resp.json()
    assert stats["total_students"] >= 3
    assert stats["total_assessments"] >= 1
    assert stats["performance_records_count"] >= 1


def test_student_cannot_perform_admin_operations():
    app.dependency_overrides[get_current_user] = mock_student_user

    # Student cannot create students
    resp1 = client.post(
        "/api/v1/academic-data/students",
        json={"enrollment_number": "HACK", "first_name": "A", "last_name": "B", "department": "CS", "admission_year": 2022, "institution_id": str(INST_A_ID), "program_id": str(PROGRAM_A_ID)},
    )
    assert resp1.status_code == 403

    # Student cannot create assessments
    resp2 = client.post(
        "/api/v1/academic-data/assessments",
        json={"assessment_name": "Hack", "maximum_marks": 50.0, "subject_id": str(SUBJECT_A_ID), "academic_year": "2024-2025", "semester": 4, "institution_id": str(INST_A_ID)},
    )
    assert resp2.status_code == 403

    # Student cannot verify records
    resp3 = client.post(
        f"/api/v1/academic-data/records/{uuid.uuid4()}/verify",
        json={"action": "VERIFY"},
    )
    assert resp3.status_code == 403

    app.dependency_overrides[get_current_user] = mock_faculty_user
