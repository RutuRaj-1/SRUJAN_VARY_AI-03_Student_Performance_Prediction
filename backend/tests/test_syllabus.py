import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser, require_roles
from app.models.enums import UserRole, AccountStatus, DocumentStatus, CompetencyCategory, IndustryImportance, BloomTaxonomyLevel
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    SyllabusDocument,
    SyllabusUnit,
    SyllabusTopic,
    LearningOutcome,
    Competency,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
)
from app.services.syllabus.document_service import document_service
from app.services.syllabus.ai_structuring_service import ai_structuring_service, classify_bloom_verb
from app.services.syllabus.competency_service import competency_service
from app.services.syllabus.industry_mapping_service import industry_mapping_service
from app.services.syllabus.gap_analysis_service import gap_analysis_service
from app.services.syllabus.review_service import review_service

# In-memory test SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_INST_ID = uuid.uuid4()
OTHER_INST_ID = uuid.uuid4()
FACULTY_USER_ID = uuid.uuid4()
STUDENT_USER_ID = uuid.uuid4()
ADMIN_USER_ID = uuid.uuid4()

SAMPLE_SYLLABUS_TEXT = """
COURSE TITLE: OPERATING SYSTEMS (CS401)
CREDITS: 4
TOTAL HOURS: 45

COURSE OUTCOMES:
CO1: Understand operating system architectures and system call interfaces.
CO2: Analyze CPU scheduling algorithms and process synchronization mechanisms.
CO3: Implement memory management techniques and virtual memory page replacement.
CO4: Design file system storage management and evaluate disk scheduling algorithms.

UNIT I: PROCESS MANAGEMENT AND THREADS (9 Hours)
Processes: Process Concept, Process Scheduling, Operations on Processes, Inter-process Communication.
Threads: Overview, Multicore Programming, Multithreading Models, Thread Libraries.
Process Concurrency: Critical-Section Problem, Peterson's Solution, Synchronization Hardware, Semaphores, Classic Problems of Synchronization, Monitors.

UNIT II: CPU SCHEDULING AND DEADLOCKS (9 Hours)
CPU Scheduling: Basic Concepts, Scheduling Criteria, Scheduling Algorithms (FCFS, SJF, Priority, Round-Robin).
Deadlocks: System Model, Deadlock Characterization, Methods for Handling Deadlocks, Deadlock Prevention, Deadlock Avoidance, Deadlock Detection, Recovery from Deadlock.

UNIT III: MEMORY MANAGEMENT (9 Hours)
Main Memory: Background, Swapping, Contiguous Memory Allocation, Segmentation, Paging, Structure of the Page Table.
Virtual Memory: Background, Demand Paging, Copy-on-Write, Page Replacement Algorithms (FIFO, LRU, Optimal), Allocation of Frames, Thrashing.

UNIT IV: STORAGE MANAGEMENT AND FILE SYSTEMS (9 Hours)
Mass-Storage Structure: Overview of Mass-Storage Structure, Disk Structure, Disk Attachment, Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN), Disk Management, Swap-Space Management.
File-System Interface: File Concept, Access Methods, Directory and Disk Structure, File-System Mounting, File Sharing, Protection.

UNIT V: CASE STUDIES AND LINUX SYSTEM PROGRAMMING (9 Hours)
Linux System: Design Principles, Kernel Modules, Process Management in Linux, Scheduling in Linux, Memory Management in Linux, File Systems in Linux, Input and Output, Interprocess Communication.
Network Structure, Security.
"""


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Create Institutions
    inst1 = Institution(
        id=TEST_INST_ID,
        name="Apex Institute of Technology",
        institution_code="AIT-TEST",
        institution_type="ENGINEERING",
        city="Bengaluru",
        state="Karnataka",
    )
    inst2 = Institution(
        id=OTHER_INST_ID,
        name="Other Technical University",
        institution_code="OTU-TEST",
        institution_type="UNIVERSITY",
        city="Mumbai",
        state="Maharashtra",
    )
    session.add_all([inst1, inst2])

    # Create Profiles
    prof_faculty = Profile(
        id=FACULTY_USER_ID,
        full_name="Prof. Alan Turing",
        email="alan.turing@ait.edu",
        role=UserRole.FACULTY.value,
        institution_id=TEST_INST_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    prof_student = Profile(
        id=STUDENT_USER_ID,
        full_name="Ada Lovelace",
        email="ada.lovelace@ait.edu",
        role=UserRole.STUDENT.value,
        institution_id=TEST_INST_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    prof_admin = Profile(
        id=ADMIN_USER_ID,
        full_name="Dr. John von Neumann",
        email="admin@ait.edu",
        role=UserRole.INSTITUTION_ADMIN.value,
        institution_id=TEST_INST_ID,
        account_status=AccountStatus.ACTIVE.value,
    )
    session.add_all([prof_faculty, prof_student, prof_admin])

    # Seed an industry role for tests
    role = IndustryRoleProfile(
        id=uuid.uuid4(),
        role_title="Software Development Engineer - Systems",
        role_family="Software Development",
        description="Systems and infrastructure software engineer.",
        experience_tier="Entry-Level / Fresher",
    )
    session.add(role)
    session.flush()

    req1 = IndustryCompetencyRequirement(
        id=uuid.uuid4(),
        role_id=role.id,
        competency_name="Process Concurrency & Thread Synchronization",
        category=CompetencyCategory.THEORETICAL.value,
        required_depth=3,
        importance=IndustryImportance.HIGH.value,
        description="Semaphores, locks, and thread concurrency control.",
    )
    req2 = IndustryCompetencyRequirement(
        id=uuid.uuid4(),
        role_id=role.id,
        competency_name="Kubernetes Container Orchestration",
        category=CompetencyCategory.TOOLS_TECHNOLOGIES.value,
        required_depth=3,
        importance=IndustryImportance.MEDIUM.value,
        description="Cloud orchestration with Kubernetes.",
    )
    session.add_all([req1, req2])

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
        user_id=str(FACULTY_USER_ID),
        email="alan.turing@ait.edu",
        role=UserRole.FACULTY,
        account_status=AccountStatus.ACTIVE,
        full_name="Prof. Alan Turing",
        institution_id=str(TEST_INST_ID),
        raw_claims={},
    )


def mock_student_user():
    return CurrentUser(
        user_id=str(STUDENT_USER_ID),
        email="ada.lovelace@ait.edu",
        role=UserRole.STUDENT,
        account_status=AccountStatus.ACTIVE,
        full_name="Ada Lovelace",
        institution_id=str(TEST_INST_ID),
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


def test_bloom_taxonomy_classification():
    assert classify_bloom_verb("Define virtual memory concepts") == BloomTaxonomyLevel.REMEMBER
    assert classify_bloom_verb("Explain thread lifecycle and states") == BloomTaxonomyLevel.UNDERSTAND
    assert classify_bloom_verb("Implement CPU scheduling in C") == BloomTaxonomyLevel.APPLY
    assert classify_bloom_verb("Analyze page replacement algorithms") == BloomTaxonomyLevel.ANALYZE
    assert classify_bloom_verb("Evaluate disk scheduling seek time") == BloomTaxonomyLevel.EVALUATE
    assert classify_bloom_verb("Design a thread-safe memory allocator") == BloomTaxonomyLevel.CREATE


def test_create_academic_program_and_subject():
    # 1. Program
    prog_resp = client.post(
        "/api/v1/syllabus/programs",
        json={
            "name": "B.Tech Computer Science & Engineering",
            "code": "BTECH-CSE",
            "degree_type": "Bachelor of Technology",
            "duration_years": 4,
            "is_active": True,
            "institution_id": str(TEST_INST_ID),
        },
    )
    assert prog_resp.status_code == 201
    prog_data = prog_resp.json()
    prog_id = prog_data["id"]

    # 2. Subject
    subj_resp = client.post(
        "/api/v1/syllabus/subjects",
        json={
            "name": "Operating Systems",
            "code": "CS401",
            "semester": 4,
            "academic_year": "2024-2025",
            "regulation_version": "R22",
            "credits": 4,
            "total_hours": 45,
            "description": "Core systems software course",
            "prerequisites": ["Data Structures", "Computer Organization"],
            "institution_id": str(TEST_INST_ID),
            "program_id": prog_id,
        },
    )
    assert subj_resp.status_code == 201
    subj_data = subj_resp.json()
    assert subj_data["code"] == "CS401"


def test_syllabus_upload_validation_rejects_invalid_file():
    bad_file = io.BytesIO(b"executable binaries")
    resp = client.post(
        "/api/v1/syllabus/upload",
        files={"file": ("malware.exe", bad_file, "application/octet-stream")},
        data={"institution_id": str(TEST_INST_ID)},
    )
    assert resp.status_code == 400
    assert "Unsupported file extension" in resp.json()["detail"]


def test_syllabus_upload_and_complete_processing_lifecycle():
    # 1. Get created subject
    subjects_resp = client.get("/api/v1/syllabus/subjects")
    assert subjects_resp.status_code == 200
    subjects = subjects_resp.json()
    assert len(subjects) > 0
    subject_id = subjects[0]["id"]

    # 2. Upload valid syllabus text
    txt_file = io.BytesIO(SAMPLE_SYLLABUS_TEXT.encode("utf-8"))
    upload_resp = client.post(
        "/api/v1/syllabus/upload",
        files={"file": ("operating_systems_syllabus.txt", txt_file, "text/plain")},
        data={"institution_id": str(TEST_INST_ID), "subject_id": subject_id},
    )
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()
    doc_id = doc_data["id"]
    assert doc_data["status"] == DocumentStatus.UPLOADED.value

    # 3. Process document (trigger extraction, AI structuring, competency classification & gap analysis)
    process_resp = client.post(f"/api/v1/syllabus/documents/{doc_id}/process")
    assert process_resp.status_code == 200
    detail = process_resp.json()
    assert detail["status"] == DocumentStatus.REVIEW_REQUIRED.value
    assert len(detail["units"]) == 5
    assert detail["units"][0]["unit_number"] == 1
    assert "PROCESS MANAGEMENT" in detail["units"][0]["title"].upper()

    # 4. Check hierarchical structure endpoint
    struct_resp = client.get(f"/api/v1/syllabus/subjects/{subject_id}/structure")
    assert struct_resp.status_code == 200
    units = struct_resp.json()
    assert len(units) == 5
    assert len(units[0]["topics"]) > 0

    # 5. Check competencies extraction & categorization
    comp_resp = client.get(f"/api/v1/syllabus/subjects/{subject_id}/competencies")
    assert comp_resp.status_code == 200
    competencies = comp_resp.json()
    assert len(competencies) > 0
    categories = {c["category"] for c in competencies}
    assert len(categories) >= 2  # multiple categories identified
    assert any("Concurrency" in c["title"] or "Process" in c["title"] for c in competencies)

    # 6. Check industry roles and gap analysis
    roles_resp = client.get("/api/v1/syllabus/industry-roles")
    assert roles_resp.status_code == 200
    assert len(roles_resp.json()) > 0

    gap_resp = client.get(f"/api/v1/syllabus/subjects/{subject_id}/gap-analysis")
    assert gap_resp.status_code == 200
    gap_summaries = gap_resp.json()
    assert len(gap_summaries) > 0

    # Find the systems engineering role summary
    systems_summary = next((s for s in gap_summaries if "Systems" in s["role_title"]), None)
    if systems_summary:
        assert systems_summary["total_industry_requirements"] == 2
        # Verify direct match on concurrency and missing on Kubernetes
        status_set = {g["status"] for g in systems_summary["gaps"]}
        assert "DIRECT" in status_set or "PARTIAL" in status_set
        assert "MISSING" in status_set
        assert systems_summary["coverage_percentage"] > 0.0

    # 7. Faculty Unit and Topic Edit
    unit_id = units[0]["id"]
    unit_patch_resp = client.patch(
        f"/api/v1/syllabus/units/{unit_id}",
        json={"title": "Unit 1: Advanced Process & Concurrency Control", "estimated_hours": 10},
    )
    assert unit_patch_resp.status_code == 200

    topic_id = units[0]["topics"][0]["id"]
    topic_patch_resp = client.patch(
        f"/api/v1/syllabus/topics/{topic_id}",
        json={"topic_name": "Modern Process Scheduling & Linux IPC"},
    )
    assert topic_patch_resp.status_code == 200

    # 8. Faculty Review Action (Approval)
    review_resp = client.post(
        f"/api/v1/syllabus/documents/{doc_id}/review",
        json={"action": "APPROVED", "comments": "Approved after comprehensive unit hours audit."},
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == DocumentStatus.APPROVED.value

    # 9. Audit History Check
    hist_resp = client.get(f"/api/v1/syllabus/documents/{doc_id}/history")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert len(hist) >= 3  # unit update, topic update, review approval
    actions = [h["action"] for h in hist]
    assert "APPROVED" in actions
    assert "UNIT_UPDATED" in actions
    assert "TOPIC_UPDATED" in actions


def test_student_cannot_review_or_edit_units():
    app.dependency_overrides[get_current_user] = mock_student_user

    # Attempt unit patch as student -> Expect 403 Forbidden
    resp = client.patch(
        f"/api/v1/syllabus/units/{uuid.uuid4()}",
        json={"title": "Hacked Unit Title"},
    )
    assert resp.status_code == 403

    # Attempt document review as student -> Expect 403 Forbidden
    resp2 = client.post(
        f"/api/v1/syllabus/documents/{uuid.uuid4()}/review",
        json={"action": "APPROVED"},
    )
    assert resp2.status_code == 403

    app.dependency_overrides[get_current_user] = mock_faculty_user
