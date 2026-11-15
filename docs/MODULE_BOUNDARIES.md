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

### Module 05: Explainable Academic Risk Prediction (Implemented & Verified — Phase 07)
- **Purpose:** Proactive early identification of students who may experience future academic difficulty using time-bounded, explainable academic evidence.
- **Responsibilities:**
  - Multi-factor risk target modeling framework (`academic_risk_targets`) with configurable institutional thresholds and prediction horizons.
  - Strict temporal slicing and anti-leakage validation engine (`leakage_validator.py`, `risk_feature_snapshots`).
  - Standardized 12-dimensional numerical feature store incorporating continuous assessment averages, trajectories, topic mastery ratios, and verified attendance rates.
  - Target variable quarantine preventing final exam marks from entering predictive feature vectors.
  - Dual-model hierarchy: L2-regularized Logistic Regression and Decision Tree with Dataset Readiness Gates, auto-falling back to deterministic expert rules when training data is insufficient.
  - Grounded explainability engine decomposing predictions into directional adverse risk factors and protective factors with verified evidence provenance traces.
  - Supabase Row-Level Security and FastAPI RBAC enforcing complete student self-isolation and strict Placement Officer firewall (§ 4.2).
- **Dependencies:** Academic Data Intelligence Hub (Phase 04 attendance and assessment records), Intelligent Assessment Engine (Phase 05 attempts), Learning Mastery & Performance Analytics (Phase 06 topic mastery and gap findings).
- **Shared With Other Modules:** Exposes time-bounded risk classifications and adverse factor attributions to Module 06 (Personalized Interventions).
- **Invariant:** Never combines risk probabilities with career readiness or mastery into an aggregate student score. Never uses demographic variables, biometrics, or invasive eye-gaze tracking. Observes strict non-stigmatization scientific governance.

---

### Module 06: Personalized Intervention & Student Growth (Implemented & Verified — Phase 08)
- **Purpose:** Transform verified academic evidence, topic mastery gaps, and predictive risk indicators into actionable, measurable, faculty-reviewed academic support plans.
- **Responsibilities:**
  - Multi-tiered recommendation engine generating evidence-grounded candidate proposals (`academic_intervention_recommendations`).
  - Specialized insufficient-evidence handling: recommending low-stakes diagnostic evaluations (`FORMATIVE_ASSESSMENT`) rather than remedial failure assumptions.
  - Institutional intervention template catalog (`intervention_templates`) with effort estimates and blueprint actions.
  - Structured academic support plans (`academic_intervention_plans`) governed by explicit state transitions (`DRAFT` $\rightarrow$ `PENDING_REVIEW` $\rightarrow$ `APPROVED` $\rightarrow$ `ACTIVE` $\rightarrow$ `COMPLETED`).
  - Action item tracking (`academic_intervention_actions`) with student evidence submissions and faculty verifications.
  - Append-only progress audit ledger (`intervention_progress_events`).
  - Observational follow-up monitoring (`intervention_outcome_observations`) strictly adhering to non-causal scientific governance.
  - Supabase Row-Level Security and FastAPI RBAC enforcing student self-isolation and Placement Officer quarantine (§ 4.2).
- **Dependencies:** AI Syllabus Intelligence (Phase 03 topics and CLOs), Academic Data Intelligence Hub (Phase 04 attendance and assessment records), Intelligent Assessment Engine (Phase 05 attempts), Learning Mastery Analytics (Phase 06 topic mastery and gap findings), Academic Risk Engine (Phase 07 predictions).
- **Shared With Other Modules:** Closes the loop on academic difficulty. Exposes intervention engagement and completion outcomes to student progress tracking.
- **Invariant:** Interventions never automate high-stakes disciplinary actions, grade penalties, or financial aid decisions. Observes strict human-in-the-loop faculty review. Never makes unsubstantiated causal claims. Observes Placement Officer quarantine.

---

### Module 07/08: Career Readiness & Industry Skill Gap Intelligence (Implemented & Verified — Phase 09)
- **Purpose:** Connect verified academic learning evidence and practical engineering projects to curated professional role benchmarks through transparent, non-aggregated intelligence.
- **Responsibilities:**
  - Curate versioned industry role profiles (`industry_role_profiles`) with competency depth requirements (`industry_competency_requirements`).
  - Human-in-the-loop mapping review governance enforcing that only faculty-approved mappings (`APPROVED`) influence authoritative scoring.
  - Student practical project evidence submission and faculty verification ledger (`student_project_evidence`).
  - Unified competency evidence synthesis (`student_competency_evidence`) across continuous topic mastery, coding assessments, and verified projects.
  - Deterministic, role-specific readiness evaluations with core and practical coverage percentages (`career_readiness_analyses`).
  - 5-tier categorized industry skill gap discovery: Demonstrated Gap, Practical Evidence Gap, Curriculum Gap, Evidence Gap, Mapping Gap (`career_skill_gap_findings`).
  - Actionable career development roadmaps (`career_development_recommendations`) decoupled from formal academic remediation.
  - Defense-in-depth Placement Officer firewall: Placement Officers access career profiles for placement matching, with zero access to Phase 07 risk data or Phase 08 confidential interventions.
- **Dependencies:** AI Syllabus Intelligence (Phase 03 competencies and roles), Academic Data & Assessment Engine (Phase 04/05 records and attempts), Learning Mastery Analytics (Phase 06 topic mastery).
- **Shared With Other Modules:** Provides unpolluted industry readiness and practical portfolio evidence to Placement Officers and students.
- **Invariant:** Never compresses student capability into an arbitrary composite employability percentage. Missing evidence is never conflated with incompetence. Placement Officer quarantine strictly preserved.

---

### Module 09: Unified Intelligence Dashboard & Cross-Module Integration (Implemented & Verified — Phase 10)
- **Purpose:** Cohesive, role-aware synthesis across all underlying modules without duplicating business logic, fabricating composite scores, or breaching tenant/privacy firewalls.
- **Responsibilities:**
  - Role-specific aggregation pipelines:
    - `StudentDashboardService`: Aggregates profile header, verified academic records, topic mastery, explainable risk with protective factors, active interventions, and career readiness alignments.
    - `FacultyDashboardService`: Aggregates teaching load, student mastery distribution, risk cohorts needing support, and review checkpoints.
    - `InstitutionDashboardService`: Executive multi-metric institutional health overview (enrollment, curriculum coverage, CLO attainment, risk distribution, intervention efficacy).
    - `PlacementDashboardService`: Career readiness matching, candidate discovery pipeline, and institutional skill shortages with active defense-in-depth firewalling.
    - `AdminDashboardService`: Platform tenant health, module utilization metrics, and append-only audit pulse.
  - Strict Placement Officer Privacy Firewall: Complete programmatic (`_assert_not_placement_officer`) and endpoint-level blocking against academic risk (Module 05) and confidential interventions (Module 06).
  - Explicit Data Freshness & Provenance Metadata: Every analytical card carries source module provenance, calculated timestamps, and freshness status (`FRESH`, `STALE`, `CACHED`).
  - Dynamic Perspective Switcher: Administrative users (`SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`) can inspect role-specific views within authorized scopes.
- **Dependencies:** Consumes read-only APIs and query pipelines from Modules 01–08.
- **Invariant:** Read-only aggregation layer. Never invents synthetic single-number student scores (e.g. "Overall Quality Index"). Never bypasses tenant scoping or row-level permissions.


