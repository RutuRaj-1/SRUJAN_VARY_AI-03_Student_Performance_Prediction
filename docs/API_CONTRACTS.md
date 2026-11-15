# MASTERY — API Contracts & Integration Conventions

**Version:** 2.0  
**Base URL:** `/api/v1`  
**Data Format:** JSON (`application/json`)  
**Phase:** 02/11 — Authentication & Identity Foundation  

---

## 1. Global API Design Conventions

### 1.1 Versioning
All domain routes reside strictly under `/api/v1`. Route naming uses lowercase, hyphen-separated kebab-case:
- Correct: `/api/v1/auth/me`
- Incorrect: `/api/v1/auth/getMe`

### 1.2 Authentication Header
All protected endpoints require the caller's Supabase JWT access token:
```http
Authorization: Bearer <access_token>
```
Tokens are validated via the Supabase project's JWKS endpoint (`ES256`).

---

## 2. Authentication & User Profile Endpoints (Phase 02)

### 2.1 Get Current Authenticated Profile
- **Endpoint:** `GET /api/v1/auth/me`
- **Security:** Requires valid Bearer JWT.
- **Description:** Returns the caller's authoritative profile, global role, account status, and effective RBAC permissions.
- **Response Schema:**
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "email": "student@institution.edu",
  "full_name": "Rohan Sharma",
  "role": "STUDENT",
  "account_status": "ACTIVE",
  "institution_id": "11111111-1111-1111-1111-111111111111",
  "permissions": [
    "profile:self:read",
    "profile:self:update",
    "assessments:attempt",
    "mastery:self:read"
  ]
}
```

### 2.2 Refresh Authoritative Profile
- **Endpoint:** `POST /api/v1/auth/refresh-profile`
- **Security:** Requires valid Bearer JWT.
- **Description:** Forces a backend database synchronization to fetch the latest role and approval status, rejecting client-side metadata overrides.

### 2.3 Get Effective Permissions
- **Endpoint:** `GET /api/v1/auth/permissions`
- **Security:** Requires valid Bearer JWT.
- **Response Schema:**
```json
{
  "role": "FACULTY",
  "permissions": [
    "syllabus:upload",
    "syllabus:approve",
    "assessments:create",
    "risk:view_alerts"
  ]
}
```

### 2.4 Update Self-Editable Profile Fields
- **Endpoint:** `PATCH /api/v1/users/me`
- **Security:** Requires valid Bearer JWT.
- **Description:** Allows modifying ONLY self-editable personal information. Ignores any client attempts to elevate role or account status.
- **Request Schema:**
```json
{
  "full_name": "Rohan K. Sharma",
  "phone": "+91 9876543210",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

### 2.5 Get User Affiliated Institution
- **Endpoint:** `GET /api/v1/institutions/me`
- **Security:** Requires valid Bearer JWT + `ACTIVE` account status.
- **Response Schema:**
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "name": "National Institute of Technology",
  "institution_code": "NIT-01",
  "institution_type": "Autonomous Engineering Institute",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "is_active": true,
  "created_at": "2026-11-15T12:00:00Z"
}
```

### 2.6 Get Institution Membership Roster
- **Endpoint:** `GET /api/v1/institutions/{institution_id}/members`
- **Security:** Requires role `INSTITUTION_ADMIN` or `SUPER_ADMIN`.
- **Description:** Returns roster of members. Institution admins are restricted strictly to their own institution.

### 2.7 Update Member Approval Status
- **Endpoint:** `PATCH /api/v1/institutions/{institution_id}/members/{user_id}`
- **Security:** Requires role `INSTITUTION_ADMIN` or `SUPER_ADMIN`.
- **Request Schema:**
```json
{
  "membership_status": "ACTIVE",
  "membership_role": "STUDENT"
}
```


---

## 3. Module 02: AI Syllabus & Competency Intelligence Endpoints (Phase 03)

### 3.1 Academic Programs & Subjects
- `POST /api/v1/syllabus/programs` — Create academic degree program (`SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`)
- `GET /api/v1/syllabus/programs` — List programs for caller's institution
- `POST /api/v1/syllabus/subjects` — Create academic course/subject (`SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`)
- `GET /api/v1/syllabus/subjects` — List subjects with optional `program_id` filtering
- `GET /api/v1/syllabus/subjects/{id}` — Get subject details, credits, hours, and prerequisites

### 3.2 Syllabus Document Ingestion & Processing
- `POST /api/v1/syllabus/upload` — Multipart form-data upload for PDF, DOCX, TXT syllabus documents
- `POST /api/v1/syllabus/documents/{id}/process` — Trigger PyMuPDF extraction, AI curriculum structuring, competency categorization, and gap analysis
- `GET /api/v1/syllabus/documents` — List uploaded documents for caller's institution
- `GET /api/v1/syllabus/documents/{id}` — Get document extraction details and hierarchical units

### 3.3 Curriculum Exploration & Competencies
- `GET /api/v1/syllabus/subjects/{id}/structure` — Get structured curriculum tree: units, estimated hours, topics, and Bloom's learning outcomes
- `GET /api/v1/syllabus/subjects/{id}/competencies` — Get competencies classified across Theoretical, Programming, Tools/Technologies, Analytical, Practical with depth (1-5) and syllabus evidence

### 3.4 Industry Alignment & Gap Analysis
- `GET /api/v1/syllabus/industry-roles` — List benchmark technical roles (Backend SDE, Full-Stack, Data Engineer, ML Engineer, DevOps) and requirements
- `GET /api/v1/syllabus/subjects/{id}/gap-analysis` — Get curriculum gap analysis summaries, coverage percentages, and explainable recommendations

### 3.5 Faculty Review & Modification Workspace
- `POST /api/v1/syllabus/documents/{id}/review` — Approve, reject, or request revisions on curriculum document with comments
- `GET /api/v1/syllabus/documents/{id}/history` — Audit trail log displaying all reviews, unit edits, and topic modifications
- `PATCH /api/v1/syllabus/units/{id}` — Faculty edit unit title, estimated hours, and description
- `PATCH /api/v1/syllabus/topics/{id}` — Faculty edit topic name and subtopics


---

## 4. Module 03: Academic Data Intelligence Hub Endpoints (Phase 04)

Base Route: `/api/v1/academic-data` (also mounted as `/academic`)

### 4.1 Overview & Metrics
- `GET /api/v1/academic-data/overview`
  - **Permissions:** All authenticated users (`STUDENT` scoped to self, others scoped to institution).
  - **Description:** Returns aggregate statistics on total students, active enrollments, assessments, verified records, attendance consistency, and open data quality issues.

### 4.2 Student Directory & Academic Profiles
- `GET /api/v1/academic-data/students`
  - **Query Params:** `search`, `department`, `semester`, `program_id`, `skip`, `limit`.
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Filterable directory of student academic profiles.
- `POST /api/v1/academic-data/students`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`.
  - **Description:** Create student academic profile with institutional enrollment number uniqueness.
- `GET /api/v1/academic-data/students/{id}`
  - **Permissions:** Self-student or authorized faculty/admin.
  - **Description:** Comprehensive academic profile containing enrollments, assessment performance history, attendance session logs, and quality flags.

### 4.3 Subject Enrollments
- `POST /api/v1/academic-data/enrollments`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`.
  - **Description:** Register student in academic subject for specific academic year and semester.
- `GET /api/v1/academic-data/enrollments`
  - **Query Params:** `student_id`, `subject_id`, `academic_year`, `semester`.
  - **Description:** Query enrollments by student, subject, or academic term.

### 4.4 Academic Assessments
- `POST /api/v1/academic-data/assessments`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Define new course assessment with maximum marks, passing marks, weightage, and type.
- `GET /api/v1/academic-data/assessments`
  - **Query Params:** `subject_id`, `academic_year`, `semester`.
  - **Description:** List configured assessments for an academic subject.

### 4.5 Performance Records & Marks
- `POST /api/v1/academic-data/marks`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Record student marks with automatic snapshot of `max_marks`, range checks (`0 <= marks <= max_marks`), and non-numeric states (`PASSED`, `FAILED`, `ABSENT`, `NOT_SUBMITTED`, `EXEMPTED`).
- `GET /api/v1/academic-data/marks`
  - **Query Params:** `student_id`, `assessment_id`, `subject_id`.
  - **Description:** Retrieve student assessment performance records with verification status.

### 4.6 Student Attendance Records
- `POST /api/v1/academic-data/attendance`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Record session-level attendance status (`PRESENT`, `ABSENT`, `LATE`, `EXCUSED`, `NOT_RECORDED`).
- `GET /api/v1/academic-data/attendance`
  - **Query Params:** `student_id`, `subject_id`, `from_date`, `to_date`.
  - **Description:** Retrieve time-series attendance records for individual student or course cohort.

### 4.7 Batch Ingestion & Import Center
- `POST /api/v1/academic-data/imports/upload`
  - **Content-Type:** `multipart/form-data`
  - **Form Fields:** `file`, `category` (`STUDENTS`, `PERFORMANCE`, `ATTENDANCE`), `academic_year`, `semester`, `subject_id`, `program_id`.
  - **Description:** Two-phase upload: validates headers, parses data rows, identifies parsing/boundary errors, and returns a staged import preview.
- `POST /api/v1/academic-data/imports/{id}/execute`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`.
  - **Description:** Executes atomic commit of staged valid rows into core academic tables.
- `GET /api/v1/academic-data/imports`
  - **Description:** List import jobs and execution logs.
- `GET /api/v1/academic-data/imports/{id}/errors`
  - **Description:** Detailed row-by-row error report for failed imports.

### 4.8 Data Quality & Anomaly Intelligence
- `POST /api/v1/academic-data/quality/scan`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Executes deterministic heuristic rules across student records, detecting marks without attendance, attendance without enrollment, unverified high-variance scores, and duplicate enrollment attempts.
- `GET /api/v1/academic-data/quality/findings`
  - **Description:** List active quality findings categorized by severity (`CRITICAL`, `ERROR`, `WARNING`, `INFO`).

### 4.9 Record Verification & Compliance Audits
- `POST /api/v1/academic-data/records/verify`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Description:** Faculty verification of marks or student profiles with audit trail logging and mandatory change justifications.
- `GET /api/v1/academic-data/audits`
  - **Description:** Append-only history of changes to academic entities.
