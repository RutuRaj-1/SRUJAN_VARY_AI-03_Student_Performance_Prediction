# Module 04: Assessment & Engagement Engine Data Model Specification

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026 (Track: AI, CyberSecurity and Digital Trust)  
**Phase:** 05/11 — Intelligent Assessment & Attentiveness Engine  
**Storage Engine:** PostgreSQL 15+ (Supabase) via SQLAlchemy 2.0 ORM  
**Migration Revision:** `9b495fb4b5d4`

---

## 1. Architectural Overview & Entity Schema Map

Module 04 introduces 10 core database entities designed to support multi-modal item authoring, assessment scheduling, attempt lifecycle tracking, rubric evaluation, and observable learning engagement telemetry.

```
                           +------------------------+
                           |   AcademicSubject      |
                           +-----------+------------+
                                       |
                +----------------------+----------------------+
                |                                             |
                v                                             v
    +------------------------+                  +---------------------------+
    |   AssessmentQuestion   |                  |    AcademicAssessment     |
    +-----------+------------+                  +-------------+-------------+
                |                                             |
   +------------+------------+                  +-------------+-------------+
   |                         |                  |                           |
   v                         v                  v                           v
+---------------------+ +---------------------------+             +-------------------+
| AssessmentQuestion  | | AssessmentQuestionMapping |             | AssessmentAttempt |
|       Option        | +---------------------------+             +---------+---------+
+---------------------+                         |                           |
                                                +-----------+               |
                                                            |               v
                                                            |     +--------------------+
                                                            |     | AssessmentResponse |
                                                            |     +---------+----------+
                                                            |               |
                                                            v               v
                                                +------------------------------+
                                                |  AssessmentRubricEvaluation  |
                                                +------------------------------+
```

---

## 2. Table Catalog & Constraint Specifications

### 2.1 `assessment_questions`
Central question repository linking items to academic subjects, syllabus units, topics, and Bloom's taxonomy cognitive levels.

| Column | Type | Nullable | Default | Description / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `uuid.uuid4()` | Primary key |
| `institution_id` | `UUID` | No | - | FK `institutions.id` (CASCADE) |
| `subject_id` | `UUID` | No | - | FK `academic_subjects.id` (CASCADE) |
| `syllabus_unit_id`| `UUID` | Yes | `NULL` | FK `syllabus_units.id` (SET NULL) |
| `syllabus_topic_id`| `UUID` | Yes | `NULL` | FK `syllabus_topics.id` (SET NULL) |
| `learning_outcome_id`| `UUID`| Yes | `NULL` | FK `learning_outcomes.id` (SET NULL) |
| `competency_id` | `UUID` | Yes | `NULL` | FK `competencies.id` (SET NULL) |
| `question_text` | `TEXT` | No | - | Natural language question prompt |
| `question_type` | `VARCHAR(50)` | No | - | `MCQ`, `MULTI_SELECT`, `TRUE_FALSE`, `SHORT_ANSWER`, `LONG_ANSWER`, `CODE_RESPONSE` |
| `difficulty` | `VARCHAR(20)` | No | `'MEDIUM'` | `EASY`, `MEDIUM`, `HARD` |
| `bloom_level` | `VARCHAR(50)` | No | `'APPLY'` | Bloom taxonomy cognitive level |
| `default_marks` | `FLOAT` | No | `1.0` | Default mark weight |
| `evaluation_method`| `VARCHAR(50)`| No | `'AUTOMATED_EXACT'`| `AUTOMATED_EXACT`, `AUTOMATED_PATTERN`, `MANUAL_RUBRIC`, `MANUAL_FACULTY`, `HYBRID` |
| `explanation` | `TEXT` | Yes | `NULL` | Faculty explanation & solution rationale |
| `expected_answer` | `TEXT` | Yes | `NULL` | Server-side ground truth |
| `code_language` | `VARCHAR(50)` | Yes | `NULL` | Execution language for coding items |
| `code_template` | `TEXT` | Yes | `NULL` | Starter boilerplate for student |
| `created_by` | `UUID` | Yes | `NULL` | FK `profiles.id` (SET NULL) |

### 2.2 `assessment_question_options`
Stores answer options for objective questions (`MCQ`, `MULTI_SELECT`, `TRUE_FALSE`).

| Column | Type | Nullable | Description / Security Constraints |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | Primary key |
| `question_id` | `UUID` | No | FK `assessment_questions.id` (CASCADE) |
| `option_text` | `TEXT` | No | Option prompt string |
| `is_correct` | `BOOLEAN` | No | **Security critical:** Stripped before delivery to students |
| `display_order` | `INTEGER` | No | Ordering in candidate view |
| `feedback` | `TEXT` | Yes | Distractor specific explanation |

### 2.3 `assessment_question_mappings`
Maps questions to assessments with custom display orders and mark weights. Enforces `UNIQUE(assessment_id, question_id)`.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary key |
| `assessment_id` | `UUID` | FK `academic_assessments.id` (CASCADE) |
| `question_id` | `UUID` | FK `assessment_questions.id` (CASCADE) |
| `display_order` | `INTEGER` | Display order in candidate exam booklet |
| `marks_allocated` | `FLOAT` | Weight of question in this assessment |
| `required` | `BOOLEAN` | Whether candidate response is mandatory |

### 2.4 `academic_assessments` (Phase 04 Model Extended)
Extended in Phase 05 with online delivery capabilities:
- `is_online_assessment`: `BOOLEAN DEFAULT TRUE`
- `duration_minutes`: `INTEGER` (Time limit)
- `start_time`: `TIMESTAMP WITH TIME ZONE` (Window opening)
- `end_time`: `TIMESTAMP WITH TIME ZONE` (Window closing)
- `instructions`: `TEXT`
- `evaluation_mode`: `VARCHAR(50)` (`AUTOMATIC`, `MANUAL`, `HYBRID`)
- `attempt_limit`: `INTEGER DEFAULT 1`
- `allow_review`: `BOOLEAN DEFAULT TRUE`

### 2.5 `assessment_attempts`
Manages the end-to-end student exam session lifecycle:
- Statuses: `IN_PROGRESS`, `PAUSED`, `SUBMITTED`, `EVALUATED`, `EXPIRED`, `CANCELLED`
- Enforces deadline checking against `deadline_at`
- Enforces student attempt quotas against `asmt.attempt_limit`

### 2.6 `assessment_responses`
Candidate answer submissions per question.
- Tracks `response_payload` (JSONB)
- Tracks `revision_count` (increments on every auto-save revision)
- Tracks `evaluation_status` (`PENDING`, `AUTO_EVALUATED`, `MANUAL_EVALUATED`, `FACULTY_REVIEW_REQUIRED`)
- Enforces uniqueness per `(attempt_id, question_id)`

### 2.7 `learning_engagement_events`
Stores transparent, observable human-computer interaction traces.
- `event_type`: `ASSESSMENT_STARTED`, `ASSESSMENT_RESUMED`, `QUESTION_VIEWED`, `ANSWER_INPUT_FOCUSED`, `ANSWER_SAVED`, `ANSWER_REVISED`, `ASSESSMENT_SUBMITTED`, `ASSESSMENT_TIMED_OUT`, `TAB_SWITCH_OBSERVED`, `SESSION_IDLE_DETECTED`
- `event_metadata`: Structured telemetry context (revisions, intervals, item targets)
- Strict privacy: Zero invasive biometric or covert surveillance signals.

---

## 3. Data Integrity & Validation Constraints

1. **Sum of Marks Constraint:**
   The sum of `marks_allocated` across all `assessment_question_mappings` for an assessment should equal `academic_assessments.maximum_marks`. This is validated prior to publishing.
2. **Student Enrollment Enforcement:**
   Candidates cannot begin an attempt for an assessment unless an active `student_subject_enrollments` record exists for `(student_id, asmt.subject_id)`.
3. **Correct Answer Key Sanitization:**
   Endpoint `/api/v1/assessments/{id}/attempts` and `/api/v1/assessments/available` project questions through `StudentQuestionView` and `StudentQuestionOptionResponse`, which strictly omit `is_correct` and `expected_answer`.
4. **Official Record Demarcation:**
   Official marks integration (`POST /api/v1/assessments/submissions/{attempt_id}/release-result`) is strictly blocked for `assessment_type == 'PRACTICE_TEST'`.
