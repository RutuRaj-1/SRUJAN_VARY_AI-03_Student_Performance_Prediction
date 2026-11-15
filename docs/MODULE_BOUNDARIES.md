# MASTERY — Module Boundaries & Inter-Domain Contracts

**Architecture Style:** Modular Monolith  
**Scope:** Seven Interconnected Business Domains  
**Phase:** 01/11 — Foundation Specification  

---

## 1. Domain Separation Principles

To prevent tight coupling and tangled dependencies across the seven modules, MASTERY enforces strict boundaries:

1. **Direct Database Isolation:** Modules interact with other domain models through domain services or explicit foreign keys, never by mutating another domain's database tables directly.
2. **Event-Ready Service Interfaces:** Service methods accept strongly typed Pydantic payloads and return validated response models.
3. **No Circular Domain Calls:** The dependency flow between modules is strictly acyclic:
   - `Academic Data (01)` & `Syllabus (02)` are foundational providers.
   - `Assessment Engine (03)` depends on Syllabus topics.
   - `Mastery Analytics (04)` consumes Academic Data (01) and Assessment results (03).
   - `Academic Risk (05)` consumes Academic Data (01) and Mastery Analytics (04).
   - `Interventions (06)` consumes Academic Risk (05) and Mastery Analytics (04).
   - `Career Readiness (07)` consumes Mastery Analytics (04) and external practical benchmarks.

---

## 2. The Seven Domain Specifications

```
+-------------------------------------------------------------------------------+
|                       MODULE DEPENDENCY FLOWCHART                             |
|                                                                               |
|   [01: Academic Data Hub]       [02: Syllabus & Competency Intelligence]      |
|             |                                     |                           |
|             |                      +--------------+                           |
|             |                      |                                          |
|             |                      v                                          |
|             |          [03: Continuous Assessment Engine]                     |
|             |                      |                                          |
|             +------------+         |                                          |
|                          |         |                                          |
|                          v         v                                          |
|                [04: Evidence Calibration & Mastery Analytics]                 |
|                          |                            |                       |
|             +------------+                            +------------+          |
|             |                                                      |          |
|             v                                                      v          |
|   [05: Academic Risk Engine]                       [07: Career Readiness]     |
|             |                                                                 |
|             v                                                                 |
|   [06: Personalized Interventions]                                            |
+-------------------------------------------------------------------------------+
```

---

### Module 01: Academic Data Intelligence Hub (Implemented & Verified — Phase 04)
- **Purpose:** Ingestion, validation, auditing, and historical timeline of institutional records.
- **Responsibilities:**
  - Student identity (`student_academic_profiles`), program assignments, and course registrations (`student_subject_enrollments`).
  - Session-level attendance records (`student_attendance_records`) with granular statuses (`PRESENT`, `ABSENT`, `LATE`, `EXCUSED`, `NOT_RECORDED`).
  - Institutional assessment marks and assignment grades (`student_assessment_records`) with score snapshotting and non-numeric states (`PASSED`, `FAILED`, `ABSENT`, `NOT_SUBMITTED`, `EXEMPTED`).
  - Two-phase staged batch data ingestion engine (`academic_import_jobs`, `academic_import_errors`) supporting CSV and XLSX formats.
  - Deterministic anomaly and data quality detection (`academic_data_quality_findings`).
  - Immutable faculty verification and compliance audit trail (`academic_record_audits`).
- **Dependencies:** Core DB infrastructure (`institutions`, `profiles`), Syllabus subjects (`academic_subjects`, `academic_programs`).
- **Shared With Other Modules:** Supplies canonical student enrollments, baseline marks, and attendance evidence to Module 03 (Assessment Engine), Module 04 (Mastery Analytics), Module 05 (Risk Prediction), and Module 06 (Interventions).
- **Invariant:** Never outputs predictive scores, risk labels, or mastery metrics; preserves pure academic evidence.

---

### Module 02: AI Syllabus & Competency Intelligence
- **Purpose:** Parsing, structuring, and mapping curriculum documents.
- **Responsibilities:**
  - Ingestion of curriculum syllabus PDFs via PyMuPDF/pdfplumber.
  - Unit and topic hierarchy extraction.
  - Learning outcome (Bloom's Taxonomy) identification.
  - Prerequisite topic dependency mapping.
  - Faculty verification workflows.
  - Industry competency bridge mapping.
- **Dependencies:** Centralized AI Service (`app.services.ai`).
- **Shared With Other Modules:** Exposes canonical `Topic` and `LearningOutcome` entities to Modules 03, 04, and 07.

---

### Module 03: Intelligent Assessment & Attentiveness Engine (Implemented & Verified — Phase 05)
- **Purpose:** Multi-modal question authoring, scheduled exam delivery, student attempt tracking, rubric evaluation, and observable interaction telemetry.
- **Responsibilities:**
  - Curriculum-aligned question bank (`assessment_questions`, `assessment_question_options`) across 6 question types, difficulty tiers, and Bloom's taxonomy cognitive levels.
  - Assessment configuration, question mapping, duration limits, and sum-of-marks validation (`academic_assessments`, `assessment_question_mappings`).
  - Student attempt session lifecycle (`assessment_attempts`), server-side deadline enforcement, and answer autosave with revision tracking (`assessment_responses`).
  - Server-side answer key protection: `is_correct` and `expected_answer` are never exposed to candidates during attempts.
  - Deterministic automated grading for objective items (MCQ, Multi-select, True/False) and faculty rubric evaluation for subjective/coding responses.
  - Phase 04 Official Gradebook integration: verified faculty marks release writes directly to `student_assessment_records` with audit logging in `academic_record_audits`. Practice tests are strictly excluded.
  - Transparent learning engagement telemetry (`learning_engagement_events`) capturing observable events governed by mandatory scientific non-attention disclaimers. Zero invasive surveillance.
- **Dependencies:** Module 01 (`student_subject_enrollments`, `academic_assessments`, `student_assessment_records`), Module 02 (`academic_subjects`, `learning_outcomes`, `competencies`), Core DB.
- **Shared With Other Modules:** Streams verified assessment results, item-level outcome demonstrations, and observable interaction telemetry to Module 04 (Evidence Calibration & Mastery Analytics).
- **Invariant:** Never outputs final topic mastery percentages, academic risk probabilities, or career readiness ratings. Observes strictly bounded evidence collection.

---

### Module 04: Learning Mastery & Performance Analytics (Implemented & Verified — Phase 06)
- **Purpose:** Evidence-based topic mastery, learning outcome attainment, and explainable performance intelligence.
- **Responsibilities:**
  - Deterministic evidence eligibility and exclusion engine preventing contaminated or duplicate inputs (`mastery_evidence_records`).
  - Precedence-based anti-double-counting guard preferring question-level granular responses over attempt aggregates.
  - Normalized topic mastery score calculation with instrument weighting, statistical sufficiency tiers, and confidence categories (`topic_mastery_results`).
  - Explicit `NULL` preservation for unassessed curriculum topics (never defaulting to 0%).
  - Course Learning Outcome (CLO) attainment aggregation against institutional target thresholds (`learning_outcome_attainment_results`).
  - Learning gap discovery distinguishing performance deficits (`PERSISTENT_LOW_SCORE`) from missing assessments (`UNASSESSED_CRITICAL_TOPIC`).
  - Longitudinal performance timelines and 6-level Bloom's Revised Taxonomy cognitive radar.
  - Mandatory scientific governance non-mastery disclaimer enforcement across all layers.
- **Dependencies:** Academic Data Intelligence Hub (Phase 04 records), Intelligent Assessment Engine (Phase 05 attempts and responses), Syllabus Intelligence (Phase 03 topics and CLOs).
- **Shared With Other Modules:** Exposes calibrated topic mastery vectors and learning gap findings to Module 05 (Academic Risk Prediction) and Module 07 (Placement Readiness).
- **Invariant:** Never computes student failure probabilities, dropout risks, career readiness ratings, or infers mastery from attendance/telemetry. Observes strictly bounded evidence evaluation.

---

### Module 05: Explainable Academic Risk Prediction
- **Purpose:** Proactive early identification of students needing academic support.
- **Responsibilities:**
  - Multi-factor risk screening combining attendance momentum, test drop-offs, and assessment lag.
  - Feature engineering pipelines across historical semesters.
  - Classical ML prediction models (Logistic Regression / Random Forest) trained solely on validated institutional data.
  - Generates explainable risk alerts detailing top contributory risk drivers.
  - Enforces faculty review checkpoints before dispatching notifications.
- **Dependencies:** Module 01 (`attendance`, `internal_marks`), Module 04 (`topic_mastery`), ML Service (`app.services.ml`).
- **Shared With Other Modules:** Triggers intervention workflows in Module 06.

---

### Module 06: Personalized Intervention & Student Growth
- **Purpose:** Prescriptive recovery roadmaps and longitudinal progress monitoring.
- **Responsibilities:**
  - AI-assisted personalized study plan generation targeting identified weak topics.
  - Prescribing remedial learning activities (targeted readings, practice problems, micro-labs).
  - Faculty or mentor approval workflow before student dispatch.
  - Mentorship assignment and progress check-in tracking.
  - Targeted reassessment and longitudinal mastery delta evaluation.
- **Dependencies:** Module 05 (`risk_alerts`), Module 04 (`topic_mastery_scores`), AI Service.
- **Shared With Other Modules:** Updates mastery confidence scores in Module 04 upon successful remedial reassessment.

---

### Module 07: Industry & Placement Readiness Intelligence
- **Purpose:** Evaluating technical capabilities against verified industry job profiles.
- **Responsibilities:**
  - Role competency framework curation (e.g. Backend Engineer, Data Analyst, Cloud DevOps).
  - Student target role selection and goal tracking.
  - Practical competency evaluations (system design, algorithmic code, database schemas).
  - External engineering evidence verification (GitHub repos, commit frequency, project complexity).
  - Skill-gap radar analytics and placement readiness indices.
- **Dependencies:** Module 02 (`competency_mappings`), Module 04 (`foundational_mastery`), External verification connectors.
- **Shared With Other Modules:** Operates independently of internal marks to provide an unpolluted industry readiness signal.
