# MASTERY — System Architecture Document

**Platform Working Title:** MASTERY — Beyond Marks. Towards Mastery.  
**System Type:** AI-Powered Student Performance Analytics, Academic Risk Prediction, and Career Readiness Platform  
**Architecture Style:** Modular Monolith (Decoupled Frontend & Backend)  
**Phase:** 02/11 — Supabase Integration, Authentication, Role-Based Access Control & Database Foundation  

---

## 1. Executive Summary & Core Philosophy

MASTERY addresses the structural shortcomings of traditional academic performance evaluation in higher education. Institutional marks (internal exam grades, attendance percentages, and assignment submissions) measure compliance and historical scoring, but frequently fail to reveal:
1. What a student actually understands conceptually.
2. Where specific topic gaps and learning impediments exist.
3. Whether a student possesses demonstrable, practical competencies required for professional industry roles.

### The Non-Aggregation Rule
The core architectural invariant of MASTERY is:
> **The three intelligence outputs — Academic Risk, Learning Mastery, and Career Readiness — must never be combined into an arbitrary aggregate student score.**

A student may be:
- At **Academic Risk** (due to missed laboratory sessions or attendance deficit) while simultaneously demonstrating **High Career Readiness** (via proven open-source software contributions and independent database architecture mastery).
- Scoring **High Internal Marks** while possessing severe **Learning Mastery Gaps** (due to rote memorization without practical synthesis capability).

---

## 2. Authentication & Identity Architecture (Phase 02)

MASTERY delegates user identity management to **Supabase Auth** while retaining strict application-level authorization, user profiling, and role-based access control on the FastAPI backend.

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT (BROWSER)                                   |
|                                                                                       |
|   1. User signs in with institutional email & password via `@supabase/supabase-js`    |
|   2. Supabase Auth validates credentials -> Returns authenticated Session & Access JWT |
|   3. Client attaches `Authorization: Bearer <access_token>` on API requests           |
+------------------------------------------+--------------------------------------------+
                                           |
                                           | HTTPS / JSON (Bearer JWT)
                                           v
+------------------------------------------+--------------------------------------------+
|                                  BACKEND API GATEWAY                                  |
|                                                                                       |
|   FastAPI Dependency (`get_current_user` / `get_current_active_user`)                 |
|                                                                                       |
|   Step 1: Parse JWT & retrieve Kid (Key ID)                                           |
|   Step 2: Fetch & verify against live Supabase JWKS (ES256 asymmetric signature)      |
|           Endpoint: `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`         |
|   Step 3: Validate issuer, audience ("authenticated"), expiration, and sub (user UUID)|
|   Step 4: Load authoritative `Profile` from PostgreSQL database                       |
|   Step 5: Enforce Account Status (`ACTIVE` required, reject `PENDING` / `SUSPENDED`)  |
|   Step 6: Enforce Role Guards (`require_roles` / `require_institution_access`)        |
+------------------------------------------+--------------------------------------------+
                                           |
                                           | Authoritative Query
                                           v
+------------------------------------------+--------------------------------------------+
|                              SUPABASE POSTGRESQL DATABASE                             |
|                                                                                       |
|   - `auth.users`: Supabase identity ledger                                            |
|   - `public.profiles`: Application identity, role, account_status, institution_id     |
|   - `public.institutions`: Multi-tenant educational institutions                     |
|   - `public.institution_memberships`: Scoped user-to-institution roles & approvals    |
|   - Row-Level Security (RLS) active on all public application tables                  |
+---------------------------------------------------------------------------------------+
```

---

## 3. Role-Based Access Control (RBAC) Matrix

| Global Role | Scope | Permitted Capabilities | Prohibited Capabilities |
| :--- | :--- | :--- | :--- |
| **SUPER_ADMIN** | Platform-Wide | Manage institutions, oversee global configuration, view all telemetry, system diagnostics | None |
| **INSTITUTION_ADMIN** | Designated Institution | Approve/suspend student and faculty accounts, manage institution settings, review institution rosters | Cross-institution modifications |
| **FACULTY** | Designated Courses & Cohorts | Upload & verify syllabus PDFs, approve AI-generated questions, review student risk alerts, manage interventions | Modifying other faculty's courses or institutional configurations |
| **PLACEMENT_OFFICER**| Designated Institution | Curate industry roles & benchmarks, evaluate placement readiness radars, verify GitHub/practical evidence | Modifying academic syllabus or internal exam marks |
| **STUDENT** | Self-Only | Take assessments, view personal topic mastery, access remedial roadmaps, track target career roles | Viewing cohort risk rosters or peer private records |

---

## 4. Multi-Layer Database Security Architecture

1. **Backend Application Layer:**
   - Every request verifies the caller's JWT signature via JWKS before executing business logic.
   - SQL queries apply explicit `WHERE user_id = :id` and `WHERE institution_id = :inst_id` filters in repositories.
2. **PostgreSQL Row-Level Security (RLS) Layer:**
   - Active on `institutions`, `profiles`, and `institution_memberships`.
   - Protects direct Supabase Client / PostgREST access so clients can only access their authorized data slice.
3. **Database Trigger Layer:**
   - `public.handle_new_user()` auto-provisions a `profiles` record on `auth.users` insert with default role `STUDENT` and status `PENDING`.
   - Never trusts client-supplied metadata for administrative privilege escalation.


---

## 5. Module 02: AI Syllabus & Competency Intelligence Architecture (Phase 03)

- **Extraction & Normalization Engine**: PyMuPDF-based PDF ingestion with rule-guided structure recovery.
- **Hierarchical Knowledge Graph**: Deconstructs syllabi into `SyllabusUnit`, `SyllabusTopic`, and granular `LearningOutcome` mapped to Bloom's Revised Taxonomy levels.
- **Bi-Directional Competency Mapping**: Bridges academic topics with real-world `Competency` nodes and industry benchmark profiles (`IndustryRoleProfile`, `IndustryCompetencyRequirement`).
- **Human-in-the-Loop Governance**: Automated AI parsing requires explicit faculty review and approval (`syllabus_review_history`) before entering the authoritative knowledge base.

---

## 6. Module 03: Academic Data Intelligence Hub Architecture (Phase 04)

- **Evidence Ingestion Subsystem**: Two-phase staged parser supporting multi-format CSV and XLSX spreadsheets with preview, validation, and atomic commit.
- **Strict Boundary Integrity**: Marks validated against `0 <= marks <= max_marks_snapshot` at schema and database check constraint levels.
- **Non-Numeric Truth Preservation**: Explicit differentiation between academic assessment failure and non-demonstration (`ABSENT`, `NOT_SUBMITTED`, `EXEMPTED`) to eliminate zero-fill skew in downstream intelligence.
- **Deterministic Quality Intelligence**: Real-time heuristic scanning flagging orphaned records, extreme grade variances, and attendance-performance discrepancies.
- **Immutable Audit Trail**: Changes to student academic records, marks, and attendance are permanently tracked in `academic_record_audits` with actor ID, timestamp, and mandatory justification.

---

## 7. Module 04: Intelligent Assessment & Attentiveness Engine Architecture (Phase 05)

- **Curriculum-Linked Question Bank**: Multi-modal item authoring (`MCQ`, `MULTI_SELECT`, `TRUE_FALSE`, `SHORT_ANSWER`, `LONG_ANSWER`, `CODE_RESPONSE`) linked to syllabus units, topics, Bloom's taxonomy tiers, and competencies.
- **Secure Online Delivery Architecture**: Scheduled assessment windows, strict duration limits, client-side countdown timer, and server-side deadline enforcement.
- **Answer Key Security Boundary**: Correct answer keys (`is_correct`, `expected_answer`) are stored server-side and completely stripped from student attempt delivery payloads.
- **Autosave & Revision Tracking**: Candidate responses are autosaved on input/selection change with atomic `revision_count` incrementing to eliminate race conditions and submission collisions.
- **Deterministic Auto-Grading & Faculty Rubrics**: Instant automated scoring for objective items; faculty evaluation queue with rubric-based scoring and feedback for subjective/coding responses.
- **Phase 04 Official Gradebook Integration**: Faculty verification writes verified assessment records to `student_assessment_records` with immutable audit logging in `academic_record_audits`. Practice tests (`PRACTICE_TEST`) are strictly barred from gradebooks.
- **Observable Interaction Telemetry**: Captures transparent, non-invasive events (`ASSESSMENT_STARTED`, `ANSWER_SAVED`, `ANSWER_REVISED`, `ASSESSMENT_SUBMITTED`) governed by mandatory scientific non-attention disclaimers. Zero biometric or covert surveillance.

---

## 8. Module 05: Learning Mastery & Performance Analytics Architecture (Phase 06)

- **Deterministic Evidence Eligibility & Exclusion**: Rigorous gateway ingesting candidate evidence from question responses, attempt totals, and imported transcripts. Rejects contaminated records with explicit exclusion reasons (`PRACTICE_MODE_UNSELECTED`, `DUPLICATE_SUPERSEDED`, `UNVERIFIED_DATA`, `ZERO_MAXIMUM_MARKS`).
- **Anti-Double-Counting Guard**: Strict hierarchy where question-level responses supersede aggregate test scores, secured by unique database constraints.
- **Explainable Topic Mastery Calculation**: Evaluates weighted normalized percentages, computes statistical sufficiency (`INSUFFICIENT`, `LIMITED`, `MODERATE`, `STRONG`) and confidence categories (`LOW`, `MEDIUM`, `HIGH`), and assigns mastery statuses (`MASTERED`, `PROGRESSING`, `NEEDS_ATTENTION`, `INSUFFICIENT_EVIDENCE`).
- **Explicit Null Preservation**: Unassessed topics and outcomes are explicitly preserved as `NULL` performance values rather than defaulting to `0%`.
- **Course Learning Outcome Attainment**: Aggregates CLO-mapped evidence against institutional threshold targets without distorting unassessed outcomes.
- **Learning Gap Discovery**: Discovers curriculum vulnerabilities, distinguishing low-performance deficits (`PERSISTENT_LOW_SCORE`) from unassessed curriculum gaps (`UNASSESSED_CRITICAL_TOPIC`).
- **Longitudinal Progressions & Bloom's Radar**: Chronological tracking of assessment events paired with 6-level Bloom's Revised Taxonomy cognitive distribution.
- **Mandatory Scientific Governance Non-Mastery Disclaimer**: Hardcoded disclaimers embedded across all schemas, API responses, and user interface panels prohibiting the conflation of assessment performance with internal student intellect.

---

## 9. Module 06: Academic Risk Prediction Engine Architecture (Phase 07)

- **Target Definitions & Horizon Policies**: Modular institutional risk target framework (`academic_risk_targets`) with configurable outcome thresholds (e.g. Midterm Deficit < 40%, CIE Deficit < 50%) and actionable prediction horizons (3–6 weeks).
- **Time-Bounded Feature Engineering**: Enforces strict observation cutoff boundaries (`recorded_at <= cutoff_date`). Slices a 12-dimensional feature store across continuous assessment averages, trajectories, topic mastery ratios, unresolved gaps, and verified attendance rates.
- **Target Quarantine & Anti-Leakage Validation**: Explicit runtime validators reject temporal leakage and quarantine milestone targets (final exam scores) from entering predictive feature vectors.
- **Dual-Model Hierarchy & Dataset Readiness Gate**: Evaluates historical labeled data against institutional readiness minimums (20 samples, 10% minority ratio). Transparently auto-falls back to deterministic expert rules when datasets are unready.
- **Grounded Feature Attributions & Explainability**: Decomposes all inferences into directional adverse risk factors and protective factors with verified evidence provenance traces.
- **Ethical AI Charter & Placement Firewall (§ 4.2)**: Placement Officers are structurally barred from accessing student risk scores via Supabase RLS and FastAPI RBAC guards. Student access is isolated strictly to self-records. Zero demographic or invasive biometric surveillance.

---

## 10. Module 07: Personalized Academic Intervention Engine Architecture (Phase 08)

- **Intervention Template Catalog**: Reusable institutional support blueprints (`intervention_templates`) covering targeted revision, adaptive practice sets, remedial workshops, 1-on-1 faculty consultations, and formative diagnostic evaluations.
- **Evidence-Grounded Recommendation Engine**: Multi-tiered decision rules translating Phase 06 topic gaps and Phase 07 adverse risk factors into structured candidate recommendations (`academic_intervention_recommendations`).
- **Insufficient Evidence Handling**: When continuous assessment evidence is insufficient ($< 2$ records), the engine strictly avoids remedial/failure assumptions and recommends a low-stakes diagnostic probe (`FORMATIVE_ASSESSMENT`).
- **Human-in-the-Loop Plan Lifecycle**: Structured state machine (`DRAFT` $\rightarrow$ `PENDING_REVIEW` $\rightarrow$ `APPROVED` $\rightarrow$ `ACTIVE` $\rightarrow$ `COMPLETED`). Recommendations require explicit faculty review before becoming official assignments.
- **Granular Action Tasks & Append-Only Progress Audit**: Actionable tasks (`academic_intervention_actions`) with instructions, effort estimates, student submission links, and faculty verification. All status changes log immutable events in `intervention_progress_events`.
- **Non-Causal Observational Follow-Up**: Subsequent assessment outcomes are recorded as empirical observations (`intervention_outcome_observations`) without unsupported causal claims.
- **Placement Officer Quarantine (§ 4.2)**: Placement Officers are strictly barred from all intervention data to eliminate recruitment bias.
