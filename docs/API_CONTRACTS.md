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

---

## 5. Module 04: Assessment & Engagement Engine API Contracts (Phase 05)

### 5.1 Question Bank
- `POST /api/v1/assessments/questions`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Payload:** `QuestionCreate` (subject_id, learning_outcome_id, question_text, question_type, difficulty, bloom_level, default_marks, explanation, options).
  - **Response:** `QuestionDetailResponse`.
- `GET /api/v1/assessments/questions`
  - **Query Params:** `subject_id`, `question_type`, `difficulty`.
  - **Description:** List questions. Faculty/Admin views include `is_correct` answer keys; student views omit them.
- `GET /api/v1/assessments/questions/{id}`
  - **Description:** Retrieve detailed question view.

### 5.2 Assessment Session Configuration
- `POST /api/v1/assessments`
  - **Permissions:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`.
  - **Payload:** `AssessmentCreate` (subject_id, assessment_name, assessment_type, maximum_marks, passing_marks, duration_minutes, attempt_limit, question_mappings).
- `GET /api/v1/assessments`
  - **Query Params:** `subject_id`, `status_filter`.
  - **Description:** List configured assessments.
- `GET /api/v1/assessments/{id}`
  - **Description:** Detailed assessment view with question mappings.
- `POST /api/v1/assessments/{id}/publish`
  - **Description:** Validates question marks sum against maximum marks and transitions status from `DRAFT` to `PUBLISHED`.
- `POST /api/v1/assessments/{id}/close`
  - **Description:** Closes assessment session (`CLOSED`).

### 5.3 Student Exam Delivery Session
- `GET /api/v1/assessments/available`
  - **Permissions:** `STUDENT`, `FACULTY`, `ADMIN`.
  - **Description:** Returns available online assessments for candidate's active enrolled subjects with attempt quotas and window statuses.
- `POST /api/v1/assessments/{id}/attempts`
  - **Description:** Initiates or resumes student attempt session. Returns candidate questions completely sanitized of answer keys (`is_correct`, `expected_answer`).
- `PUT /api/v1/assessments/attempts/{attempt_id}/responses`
  - **Payload:** `ResponseSaveRequest` (question_id, response_payload).
  - **Description:** Autosaves candidate answer, increments `revision_count`, and emits `ANSWER_SAVED` or `ANSWER_REVISED` telemetry.
- `POST /api/v1/assessments/attempts/{attempt_id}/submit`
  - **Description:** Finalizes student submission, triggers deterministic auto-grading for objective questions, and sets status to `SUBMITTED` or `EVALUATED`.

### 5.4 Faculty Evaluation & Gradebook Integration
- `GET /api/v1/assessments/{id}/submissions`
  - **Description:** Returns submissions queue for faculty grading.
- `POST /api/v1/assessments/submissions/{attempt_id}/evaluate`
  - **Payload:** `BatchEvaluationRequest` (evaluations: [{question_id, marks_awarded, feedback}], overall_remarks).
  - **Description:** Saves faculty marks and feedback for subjective items.
- `POST /api/v1/assessments/submissions/{attempt_id}/release-result`
  - **Payload:** `ReleaseResultRequest` (publish_to_official_records, verification_remarks).
  - **Description:** Writes verified marks to Phase 04 `student_assessment_records` with audit trail logging in `academic_record_audits`. Blocks practice tests from gradebook.

### 5.5 Analytics & Learning Engagement Telemetry
- `GET /api/v1/assessments/{id}/analytics`
  - **Description:** Metrics including completion rate, average score, pass rate, score distribution, and learning outcome coverage.
- `GET /api/v1/assessments/{id}/engagement-summary`
  - **Description:** Aggregated non-invasive telemetry event breakdown and mandatory scientific non-attention disclaimer.
- `POST /api/v1/assessments/engagement/events`
  - **Description:** Ingests client interaction telemetry (`ASSESSMENT_STARTED`, `ANSWER_SAVED`, `ANSWER_REVISED`, `ASSESSMENT_SUBMITTED`, etc.).

---

## 6. Module 05: Learning Mastery & Performance Analytics API

Base URL: `/api/v1/mastery`

### 6.1 Analysis Jobs
- `POST /api/v1/mastery/jobs/trigger`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Payload:** `MasteryJobTriggerRequest` (`subject_id`, `target_student_id`, `job_type`, `include_practice`, `min_evidence_threshold`)
  - **Description:** Ingests eligible assessment/gradebook evidence and recalculates topic mastery and outcome attainment.

### 6.2 Student Mastery Intelligence
- `GET /api/v1/mastery/students/{student_id}/subjects/{subject_id}/profile`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
  - **Description:** Returns overall demonstrated mastery, topic list with sufficiency badges, CLO attainment, and identified learning gaps.
- `GET /api/v1/mastery/students/{student_id}/subjects/{subject_id}/trends`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
  - **Description:** Chronological progression of assessment scores and 6-level Bloom's Revised Taxonomy cognitive radar.

### 6.3 Cohort Intelligence
- `GET /api/v1/mastery/cohort/subjects/{subject_id}/summary`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Description:** Cohort-wide enrollment analytics, curriculum coverage percentage, and topic aggregate performance.

### 6.4 Evidence Auditing & Traceability
- `GET /api/v1/mastery/topics/{result_id}/evidence`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
  - **Description:** Itemized list of contributing evidence records with marks, weights, and cognitive tiers.
- `GET /api/v1/mastery/topics/{result_id}/excluded-evidence`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
  - **Description:** Audited list of excluded candidate records with deterministic exclusion reason codes.

---

## 7. Module 06: Academic Risk Prediction API

Base URL: `/api/v1/risk`

### 7.1 Risk Targets
- `GET /api/v1/risk/targets`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT`
  - **Query:** `subject_id` (optional UUID)
  - **Description:** List configured risk targets, passing thresholds, and prediction horizons.
- `POST /api/v1/risk/targets`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Payload:** `AcademicRiskTargetCreate` (`subject_id`, `target_code`, `target_name`, `outcome_definition`, `positive_label_definition`, `passing_threshold_percentage`, `prediction_horizon_weeks`, `is_institution_policy`)
  - **Description:** Configure a new academic risk milestone definition.
- `GET /api/v1/risk/targets/{target_id}`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT`
  - **Description:** Retrieve target details.

### 7.2 Dataset Readiness & Governance
- `GET /api/v1/risk/readiness`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Query:** `subject_id`, `target_id`, `cutoff_date`
  - **Description:** Evaluates labeled sample count and minority representation. Reports whether dataset is ready for ML training.

### 7.3 Model Versions & Training
- `POST /api/v1/risk/models/train`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Query:** `subject_id`
  - **Payload:** `RiskModelTrainRequest` (`target_id`, `model_type`, `version_tag`, `hyperparameters`, `cutoff_date`)
  - **Description:** Fits ML model (Logistic Regression / Decision Tree) or auto-falls back to deterministic rules if dataset unready.
- `GET /api/v1/risk/models`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Query:** `target_id`
  - **Description:** List registered model versions.
- `POST /api/v1/risk/models/{model_version_id}/activate`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Description:** Promotes a model version to active production inference.

### 7.4 Inference & Explainability
- `POST /api/v1/risk/predictions/generate`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Payload:** `RiskPredictionGenerateRequest` (`subject_id`, `target_id`, `model_version_id`, `target_student_id`, `cutoff_date`)
  - **Description:** Extracts time-bounded feature snapshot, executes inference, and generates grounded factor attributions.
- `GET /api/v1/risk/students/{student_id}/subjects/{subject_id}/profile`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only; Placement Officers barred)
  - **Description:** Student risk profile, calibrated deficit probability, evidence sufficiency, and adverse factor list.
- `GET /api/v1/risk/cohort/subjects/{subject_id}/summary`
  - **Access:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
  - **Description:** Cohort-wide risk distribution and student roster ledger.

---

## 8. Module 07: Personalized Academic Intervention API

Base URL: `/api/v1/interventions`

### 8.1 Intervention Templates
- `GET /api/v1/interventions/templates`
  - **Access:** `STUDENT`, `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `subject_id` (optional), `intervention_type` (optional)
  - **Description:** List approved intervention templates.
- `POST /api/v1/interventions/templates`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `InterventionTemplateCreate` (`template_code`, `template_name`, `intervention_type`, `target_level`, `suggested_duration_hours`, `suggested_completion_days`, `recommended_actions_template`, `required_resources`)
  - **Description:** Create an institutional intervention blueprint.

### 8.2 Recommendations
- `POST /api/v1/interventions/recommendations/generate`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `InterventionRecommendationGenerateRequest` (`student_id`, `subject_id`, `topic_id`, `template_id`)
  - **Description:** Synthesizes Phase 06 learning gaps, unassessed topics, and Phase 07 risk factors into candidate recommendations.
- `GET /api/v1/interventions/recommendations`
  - **Access:** `STUDENT` (Self only), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `student_id`, `subject_id`, `status`
  - **Description:** List recommendations.

### 8.3 Intervention Plans
- `POST /api/v1/interventions/plans`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `InterventionPlanCreate` (`student_id`, `subject_id`, `topic_id`, `recommendation_id`, `plan_title`, `learning_objective`, `target_completion_date`, `initial_actions`)
  - **Description:** Author an academic intervention plan queued for faculty review.
- `GET /api/v1/interventions/plans`
  - **Access:** `STUDENT` (Self only; approved/active/completed only), `FACULTY`, `ADMIN`
  - **Query:** `student_id`, `subject_id`, `status`
  - **Description:** List intervention plans.
- `GET /api/v1/interventions/plans/{plan_id}`
  - **Access:** `STUDENT` (Self only), `FACULTY`, `ADMIN`
  - **Description:** Detailed plan inspector with action items and progress event history.
- `POST /api/v1/interventions/plans/{plan_id}/review`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `InterventionPlanReviewRequest` (`decision`: "APPROVE" | "REJECT", `review_notes`)
  - **Description:** Faculty review checkpoint authorizing or rejecting plan.
- `POST /api/v1/interventions/plans/{plan_id}/assign`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Description:** Promotes plan to ACTIVE and dispatches actions to student.

### 8.4 Action Tasks & Progress
- `POST /api/v1/interventions/actions/{action_id}/status`
  - **Access:** `STUDENT` (Start work, submit evidence), `FACULTY` (Verify completion)
  - **Payload:** `InterventionActionStatusUpdate` (`new_status`, `student_completion_notes`, `student_submission_url`, `faculty_feedback`)
  - **Description:** Updates action status with append-only progress event logging.

### 8.5 Outcomes & Dashboards
- `POST /api/v1/interventions/plans/{plan_id}/outcomes`
  - **Access:** `FACULTY`, `ADMIN`
  - **Payload:** `InterventionOutcomeCreate` (`baseline_mastery_percentage`, `followup_assessment_id`, `followup_score_obtained`, `followup_maximum_marks`, `observation_notes`)
  - **Description:** Records post-intervention observational evidence.
- `GET /api/v1/interventions/dashboard/faculty`
  - **Access:** `FACULTY`, `ADMIN`
  - **Query:** `subject_id`
  - **Description:** Aggregate faculty intervention metrics and priority queues.
- `GET /api/v1/interventions/dashboard/student`
  - **Access:** `STUDENT`
  - **Description:** Personalized student workspace with assigned actions checklist.

---

## 9. Module 08: Career Readiness & Industry Skill Gap Intelligence Contracts (Phase 09)

### 9.1 Role Profiles & Requirements
- `GET /api/v1/career-readiness/roles`
  - **Access:** All authenticated users (`STUDENT`, `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`)
  - **Query:** `include_inactive` (boolean)
  - **Description:** Lists permitted career role profiles with requirements.
- `GET /api/v1/career-readiness/roles/{role_id}`
  - **Access:** All authenticated users
  - **Description:** Detailed role profile with required competencies, Bloom depth levels, and importance tiers.
- `POST /api/v1/career-readiness/roles`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `IndustryRoleProfileCreate`
  - **Description:** Create an institutional role benchmark.
- `PUT /api/v1/career-readiness/roles/{role_id}`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `IndustryRoleProfileUpdate`
  - **Description:** Update role benchmark details or version.
- `POST /api/v1/career-readiness/roles/{role_id}/requirements`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `IndustryCompetencyRequirementCreate`
  - **Description:** Add benchmark competency requirement.

### 9.2 Practical Project Evidence
- `GET /api/v1/career-readiness/projects`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER` (Verified only)
  - **Query:** `student_id` (required for staff/placement)
  - **Description:** List student practical engineering projects.
- `POST /api/v1/career-readiness/projects`
  - **Access:** `STUDENT`, `FACULTY` (on-behalf)
  - **Payload:** `StudentProjectEvidenceCreate` (`title`, `description`, `technology_stack`, `repository_url`, `portfolio_url`, `demonstrated_competencies`)
  - **Description:** Submit project evidence for faculty verification.
- `PUT /api/v1/career-readiness/projects/{project_id}`
  - **Access:** `STUDENT` (Owner only, prior to verification)
  - **Payload:** `StudentProjectEvidenceUpdate`
  - **Description:** Edit submitted project details.
- `POST /api/v1/career-readiness/projects/{project_id}/review`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Payload:** `StudentProjectEvidenceReview` (`verification_status`: "VERIFIED" | "REJECTED", `verification_notes`)
  - **Description:** Faculty verification of practical projects registering verified competency credit.

### 9.3 Competency Evidence Ledger
- `GET /api/v1/career-readiness/evidence`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`
  - **Query:** `student_id`
  - **Description:** Traceable ledger of student competencies across exams, topic mastery, and verified projects.

### 9.4 Readiness Analysis & Role Comparison
- `POST /api/v1/career-readiness/analyze`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`
  - **Payload:** `CareerReadinessAnalysisRequest` (`role_id`, `student_id`, `force_recalculate`)
  - **Description:** Deterministic role readiness analysis with core/practical coverage and non-aggregation disclaimer.
- `GET /api/v1/career-readiness/compare`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`
  - **Query:** `student_id`, `role_ids`
  - **Description:** Side-by-side comparison of student standing across multiple career roles.
- `GET /api/v1/career-readiness/overview`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`
  - **Query:** `student_id`
  - **Description:** Aggregated workspace metrics (enrolled roles, demonstrated skills, active gaps).

### 9.5 Recommendations
- `GET /api/v1/career-readiness/recommendations`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`
  - **Query:** `student_id`, `role_id`
  - **Description:** List personalized skill gap development roadmaps.
- `PATCH /api/v1/career-readiness/recommendations/{recommendation_id}`
  - **Access:** Authenticated (`STUDENT` updates status/notes; `FACULTY` adds feedback)
  - **Payload:** `CareerDevelopmentRecommendationUpdate`
  - **Description:** Track roadmap execution.

---

## 10. Module 09: Unified Intelligence Dashboard Contracts (Phase 10)

Cross-module aggregation and role-aware analytical overviews adhering to tenant scoping, zero synthetic score fabrication, and the strict Placement Officer privacy firewall.

### 10.1 Student Intelligence Dashboard
- `GET /api/v1/dashboard/student/overview`
  - **Access:** `STUDENT` (Self only), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` (Strictly blocked for `PLACEMENT_OFFICER` with 403)
  - **Query:** `student_id` (optional for staff/admins, defaults to authenticated user's student profile)
  - **Description:** Returns holistic student intelligence combining academic performance records, mastery analytics, explainable risk prediction with protective factors, active intervention plans, and career readiness alignments.
- `GET /api/v1/dashboard/student/academic-performance`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN` (Blocked for `PLACEMENT_OFFICER`)
  - **Query:** `student_id`
  - **Description:** Aggregates verified course marks, total evaluations, and attendance rates with data provenance timestamps.
- `GET /api/v1/dashboard/student/mastery-summary`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN` (Blocked for `PLACEMENT_OFFICER`)
  - **Query:** `student_id`
  - **Description:** Breakdown of demonstrated, developing, and insufficient evidence syllabus topics with CLO attainment percentage.
- `GET /api/v1/dashboard/student/risk-summary`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN` (Strictly blocked for `PLACEMENT_OFFICER` with 403)
  - **Query:** `student_id`
  - **Description:** Explainable academic risk classification, probability, adverse and protective factors, and ethics disclaimer.
- `GET /api/v1/dashboard/student/intervention-summary`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN` (Strictly blocked for `PLACEMENT_OFFICER` with 403)
  - **Query:** `student_id`
  - **Description:** Active, completed, and pending intervention plan counts, high-priority actions, and faculty review checkpoints.
- `GET /api/v1/dashboard/student/career-summary`
  - **Access:** `STUDENT` (Self), `FACULTY`, `ADMIN`, `PLACEMENT_OFFICER`
  - **Query:** `student_id`
  - **Description:** Career role readiness alignments, verified project counts, demonstrated competencies, and active skill gaps.

### 10.2 Faculty Course Intelligence Dashboard
- `GET /api/v1/dashboard/faculty/overview`
  - **Access:** `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `subject_id` (optional filter)
  - **Description:** Faculty teaching intelligence across assigned courses, enrolled students, mastery distribution, risk cohorts, pending interventions, and practical project verifications.
- `GET /api/v1/dashboard/faculty/course-distribution`
  - **Access:** `FACULTY`, `ADMIN`
  - **Query:** `subject_id`
  - **Description:** Subject-level student mastery tier distributions and average assessment score summaries.
- `GET /api/v1/dashboard/faculty/risk-cohort`
  - **Access:** `FACULTY`, `ADMIN`
  - **Query:** `subject_id`
  - **Description:** Actionable list of high and moderate risk students requiring targeted pedagogical support.
- `GET /api/v1/dashboard/faculty/pending-reviews`
  - **Access:** `FACULTY`, `ADMIN`
  - **Description:** Workflow inbox of intervention plans awaiting faculty authorization and student projects pending verification.

### 10.3 Institution Executive Dashboard
- `GET /api/v1/dashboard/institution/overview`
  - **Access:** `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `department`, `academic_year`
  - **Description:** Institution-wide executive intelligence across total enrollment, curriculum coverage, CLO attainment, risk distribution, intervention efficacy rates, and industry alignment stats.
- `GET /api/v1/dashboard/institution/program-benchmarks`
  - **Access:** `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `department`
  - **Description:** Program and department-level aggregated attainment benchmarks and accreditation readiness indicators.
- `GET /api/v1/dashboard/institution/intervention-effectiveness`
  - **Access:** `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Description:** Quantified efficacy of completed academic intervention plans with baseline vs. follow-up mastery gains.

### 10.4 Placement Officer Career & Skill Intelligence Dashboard (Firewalled)
- `GET /api/v1/dashboard/placement/overview`
  - **Access:** `PLACEMENT_OFFICER`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `role_id`, `department`
  - **Description:** Ethical career intelligence aggregating role profile demand, industry skill alignments, verified practical portfolios, and institutional skill shortages. Zero exposure of academic risk, failed grades, or confidential interventions.
- `GET /api/v1/dashboard/placement/candidate-pipeline`
  - **Access:** `PLACEMENT_OFFICER`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `role_id` (required), `min_alignment_status`
  - **Description:** Candidate search matching students to career roles strictly based on verified competency mastery and project portfolios.
- `GET /api/v1/dashboard/placement/institutional-skill-gaps`
  - **Access:** `PLACEMENT_OFFICER`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`
  - **Query:** `department`
  - **Description:** Macro industry skill shortages identified across student cohorts to advise curriculum review committees.

### 10.5 Platform Super-Administrator Dashboard
- `GET /api/v1/dashboard/admin/overview`
  - **Access:** `SUPER_ADMIN`
  - **Description:** Platform health overview across registered institutions, multi-tenant user counts, module utilization stats, and audit event volume.
- `GET /api/v1/dashboard/admin/tenant-summary`
  - **Access:** `SUPER_ADMIN`
  - **Description:** Multi-tenant usage distribution across active institutions.
- `GET /api/v1/dashboard/admin/audit-pulse`
  - **Access:** `SUPER_ADMIN`
  - **Query:** `limit` (default: 50)
  - **Description:** Real-time chronological audit event log capturing administrative changes and security checkpoints.

