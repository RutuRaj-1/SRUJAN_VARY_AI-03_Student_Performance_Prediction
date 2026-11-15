"""
MASTERY — Performance Benchmarking Harness.
Measures latency (median, p95), request throughput, and error rates
across all 5 role-based unified dashboard endpoints.
"""

import os
import sys
import time
import statistics
import uuid

# Robust path resolution: works whether executed from root, scripts/, or backend/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_current_user, CurrentUser
from app.models.enums import UserRole, AccountStatus
from app.models.profile import Profile
from app.models.institution import Institution
from app.models.syllabus import AcademicProgram
from app.models.academic_data import StudentAcademicProfile
from app.db.session import get_session_local

session_factory = get_session_local()
if not session_factory:
    print("[ERROR] Database session factory could not be constructed.")
    print("Please ensure DATABASE_URL is configured in backend/.env.")
    sys.exit(1)

client = TestClient(app)

# Allow iterations to be set via CLI or env (default to 15 for responsive CLI benchmark)
ITERATIONS = int(os.environ.get("BENCHMARK_ITERATIONS", "15"))
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    ITERATIONS = int(sys.argv[1])

# Setup temporary test identity records in active db for benchmarking
db = session_factory()
inst_id = uuid.uuid4()
prog_id = uuid.uuid4()
student_user_id = uuid.uuid4()
student_acad_id = uuid.uuid4()

prof = None
inst = None
prog = None
sap = None

try:
    prof = Profile(
        id=student_user_id,
        email=f"bench_{str(uuid.uuid4())[:6]}@mastery.edu",
        full_name="Bench Student",
        role=UserRole.STUDENT.value,
    )
    inst = Institution(
        id=inst_id,
        name="Benchmark Performance University",
        institution_code=f"BPU-{str(uuid.uuid4())[:4].upper()}",
        city="Pune",
        state="Maharashtra",
    )
    prog = AcademicProgram(
        id=prog_id,
        institution_id=inst_id,
        name="B.Tech Computer Science",
        code=f"CS-BPU-{str(uuid.uuid4())[:4].upper()}",
        degree_type="UNDERGRADUATE",
        duration_years=4,
    )
    sap = StudentAcademicProfile(
        id=student_acad_id,
        profile_id=student_user_id,
        institution_id=inst_id,
        program_id=prog_id,
        enrollment_number=f"ENR-BPU-{str(uuid.uuid4())[:6].upper()}",
        first_name="Bench",
        last_name="Student",
        email=prof.email,
        department="Computer Science",
        admission_year=2024,
        current_semester=5,
        academic_status="ENROLLED",
    )
    db.add_all([prof, inst, prog, sap])
    db.commit()

    endpoints = [
        ("/api/v1/dashboard/student/overview?student_id=" + str(student_acad_id), UserRole.STUDENT, student_user_id),
        ("/api/v1/dashboard/faculty/overview", UserRole.FACULTY, uuid.uuid4()),
        ("/api/v1/dashboard/institution/overview", UserRole.INSTITUTION_ADMIN, uuid.uuid4()),
        ("/api/v1/dashboard/placement/overview", UserRole.PLACEMENT_OFFICER, uuid.uuid4()),
        ("/api/v1/dashboard/admin/overview", UserRole.SUPER_ADMIN, uuid.uuid4()),
    ]

    results = {}
    print(f"Executing {ITERATIONS} warmup and measurement iterations per endpoint...")

    for ep, role, uid in endpoints:
        times = []
        errors = 0

        current = CurrentUser(
            user_id=str(uid),
            email=f"{role.value.lower()}@bench.edu",
            role=role,
            account_status=AccountStatus.ACTIVE,
            full_name=f"Bench {role.value}",
            institution_id=str(inst_id),
        )
        app.dependency_overrides[get_current_user] = lambda c=current: c

        # Warmup calls
        for _ in range(2):
            client.get(ep)

        # Measurement calls
        for _ in range(ITERATIONS):
            t0 = time.perf_counter()
            resp = client.get(ep)
            elapsed = (time.perf_counter() - t0) * 1000.0
            if resp.status_code == 200:
                times.append(elapsed)
            else:
                errors += 1

        endpoint_name = ep.split("?")[0]
        if times:
            times.sort()
            median = statistics.median(times)
            p95 = times[int(len(times) * 0.95)]
            min_ms = min(times)
            max_ms = max(times)
        else:
            median = 0.0
            p95 = 0.0
            min_ms = 0.0
            max_ms = 0.0

        results[endpoint_name] = {
            "role": role.value,
            "median_ms": round(median, 2),
            "p95_ms": round(p95, 2),
            "min_ms": round(min_ms, 2),
            "max_ms": round(max_ms, 2),
            "errors": errors,
            "requests": ITERATIONS,
        }

    print("\n" + "=" * 80)
    print(f"{'Endpoint':<45} | {'Role':<17} | {'Median':<8} | {'p95':<8} | {'Errors'}")
    print("=" * 80)
    for ep, data in results.items():
        print(f"{ep:<45} | {data['role']:<17} | {data['median_ms']:>6.2f}ms | {data['p95_ms']:>6.2f}ms | {data['errors']}/{data['requests']}")
    print("=" * 80)

except Exception as exc:
    print(f"[ERROR] Benchmark execution encountered an error: {exc}")
    raise
finally:
    # Clean up temporary test records to leave the database clean
    try:
        if sap:
            db.delete(sap)
        if prog:
            db.delete(prog)
        if inst:
            db.delete(inst)
        if prof:
            db.delete(prof)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
