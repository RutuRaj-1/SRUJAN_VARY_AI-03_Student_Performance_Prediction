# Phase 07 Pre-Implementation Audit: Academic Risk Prediction Engine

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Phase:** 07/11  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Date:** 2026-11-15  
**Auditor:** Senior Software Architect & AI Systems Engineer  

---

## 1. Executive Summary & Repository Status

Prior to commencing development of **Module 06: Academic Risk Prediction**, a mandatory pre-implementation audit was conducted to inspect the actual repository, git branch, live database state, Alembic migrations, ML dependencies, and Phase 06 integration surfaces.

### Repository Status
- **Current Git Branch:** `feature/phase-07-academic-risk` (Cleanly branched from `main` commit `661e4a8`).
- **Base Commit:** `661e4a8` (`feat(mastery): implement Module 05 Learning Mastery & Performance Analytics (Phase 06/11)`).
- **Working Tree:** Clean, uncorrupted, no uncommitted changes.
- **Header Invariant:** Lines 1–3 of `README.md` verified preserved (`Team VARY : SRUJAN 2026`, `PS : AI-03`, `Track : AI , CyberSecurity and Digital Trust`).

---

## 2. Live Supabase PostgreSQL & Alembic Migration Audit

- **Target Database:** Supabase AWS South Asia (`ap-south-1.pooler.supabase.com:5432/postgres`).
- **Current Alembic Revision:** `992978c931de (head)`.
- **Database Tables Inventory:** 40 total tables (39 application domain tables + 1 `alembic_version`).
- **Row-Level Security (RLS) Status:** 100% active. All 39 application tables have `rowsecurity = true` and `forcerowsecurity = true`.
- **Network Latency:** ~185ms round-trip to PostgreSQL connection pooler.

### Existing Domain Table Breakdown:
- **Core Identity & Tenancy (Phase 01/02):** `institutions`, `profiles`, `institution_memberships`.
- **AI Syllabus & Competency Intelligence (Phase 03):** `academic_programs`, `academic_subjects`, `syllabus_documents`, `syllabus_units`, `syllabus_topics`, `learning_outcomes`, `competencies`, `subject_competency_mappings`, `industry_role_profiles`, `industry_competency_requirements`, `syllabus_review_history`.
- **Academic Data Intelligence Hub (Phase 04):** `student_academic_profiles`, `student_subject_enrollments`, `academic_attendance_ledgers`, `student_assessment_records`, `academic_record_audits`, `academic_import_jobs`, `data_quality_issues`.
- **Intelligent Assessment & Attentiveness Engine (Phase 05):** `academic_assessments`, `assessment_questions`, `assessment_question_options`, `assessment_question_mappings`, `assessment_attempts`, `assessment_responses`, `assessment_rubric_criteria`, `assessment_rubric_evaluations`, `learning_engagement_events`.
- **Learning Mastery & Performance Analytics (Phase 06):** `mastery_analysis_jobs`, `mastery_evidence_records`, `topic_mastery_results`, `learning_outcome_attainment_results`, `learning_gap_findings`.

---

## 3. Phase 06 Service & Data Integration Verification

To strictly prevent business logic duplication:
1. **Reuse, Don't Recompute:** Module 06 must ingest topic mastery status, sufficiency levels, CLO attainment percentages, and learning gap findings directly from `topic_mastery_results`, `learning_outcome_attainment_results`, and `learning_gap_findings`.
2. **Explicit Null Preservation:** Unassessed topics and CLOs have `demonstrated_percentage = NULL` and `sufficiency_level = INSUFFICIENT`. The risk prediction feature pipeline must never convert `NULL` to `0.0%` or treat missing evaluations as confirmed academic failure.
3. **Evidence Sufficiency Respect:** Predictions must report evidence sufficiency (`INSUFFICIENT`, `LIMITED`, `MODERATE`, `STRONG`) and output `INSUFFICIENT_EVIDENCE` status when evidence is inadequate.
4. **Anti-Double-Counting Respect:** Phase 06 already handles the precedence of question responses over attempt aggregates. Feature engineering in Phase 07 will build upon verified records.

---

## 4. ML Service Architecture & Dependency Audit

- **Existing Placeholder:** `backend/app/services/ml/service.py` contained an uninitialized class placeholder (`MLRiskPredictionService`).
- **Installed Stack:** Python 3.14.2, `numpy 2.5.4`, `scikit-learn 1.9.1`, `scipy 1.18.1`.
- **Model Philosophy:** Transparent baseline first (deterministic rule-based indicator, Logistic Regression, interpretable Decision Tree). Complex black-box ensembles (XGBoost/Neural Networks) are prohibited without empirical validation of superior performance.
- **No LLM Risk Prediction:** Large Language Models must never output numerical risk scores, failure probabilities, or synthetic student profiles.

---

## 5. Prediction Target & Temporal Leakage Prevention Audit

- **Core Rule:** Define the prediction target before training any model.
- **Target Specification:**
  - Configurable institutional targets stored in `academic_risk_targets`.
  - Primary Default Target: `COURSE_FAILURE_OR_CRITICAL_DEFICIT` (Final subject marks below institutional passing threshold, e.g., $< 50\%$ or $< 40\%$, as defined by the institution).
  - Explicit Prediction Cutoff: Feature snapshots must enforce a strict `observation_cutoff_date`.
- **Temporal Leakage Prevention:**
  - No features derived from records verified after the prediction cutoff.
  - Final exam scores or end-semester outcomes cannot be used as features when predicting that same outcome.
  - Attendance or continuous assessments occurring after the cutoff are barred.
  - Training/validation splits must be grouped by student or temporal academic periods to avoid leaking identical student trajectories between train and test sets.

---

## 6. Access Control & Tenancy Isolation

- **RBAC Matrix:**
  - `SUPER_ADMIN`: Platform governance, model registry monitoring.
  - `INSTITUTION_ADMIN`: Institutional target configuration, model deployment oversight.
  - `FACULTY`: Scoped strictly to assigned subjects and enrolled students.
  - `STUDENT`: Read-only access strictly to own prediction, understandable explanation, and limitations.
  - `PLACEMENT_OFFICER`: No access to academic risk predictions (Placement readiness is an independent module).
- **PostgreSQL Row-Level Security:** Every new Phase 07 table must implement tenant isolation with RLS policies covering `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, and `STUDENT`.

---

## 7. Audit Conclusion & Go-Ahead

The workspace and database are in an ideal state. Branch `feature/phase-07-academic-risk` is ready for implementation of Phase 07 entities, feature engineering pipelines, model training and evaluation services, prediction endpoints, RLS policies, automated tests, and the frontend workspace.
