# MASTERY — Unified Metric Dictionary
## Standardized Metric Definitions, Provenance & Semantics

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 10/11 — Unified Intelligence Dashboard & Cross-Module Integration  

---

## 1. Foundational Semantic Distinctions

MASTERY maintains strict boundaries between disparate educational dimensions:

1. **Marks $\neq$ Mastery:**  
   Marks obtained on an internal exam reflect marks awarded under test conditions. Mastery reflects demonstrated understanding across specific syllabus topics weighted by Bloom taxonomy depth.
2. **Risk $\neq$ Failure:**  
   An academic risk classification (`HIGH`, `MODERATE`) denotes statistical vulnerability under observed historical trends prior to a prediction cutoff. It is never a statement of guaranteed student failure or fixed capability.
3. **Correlation $\neq$ Causation:**  
   Observed improvements following an academic intervention plan demonstrate positive academic recovery, but do not prove that the intervention was the sole causal determinant.
4. **Readiness $\neq$ Employment Guarantee:**  
   Career alignment reflects current coverage against curated role competency frameworks. It does not constitute an employability score or hiring guarantee.
5. **Missing Evidence $\neq$ Zero:**  
   Unassessed topics or competencies are classified as `INSUFFICIENT_EVIDENCE` or `NOT_ASSESSED`. They are never coerced into a score of $0.0\%$.

---

## 2. Comprehensive Metric Dictionary

### 2.1 Academic Performance Metrics

#### Average Marks (`average_marks`)
- **Business Meaning:** Mean percentage score across verified institutional assessments.
- **Source Module:** Module 03 (Academic Data Intelligence Hub).
- **Source Entity:** `StudentAssessmentRecord` (`marks_obtained`, `maximum_marks_snapshot`).
- **Calculation:** $\frac{1}{N} \sum_{i=1}^{N} \left(\frac{\text{marks\_obtained}_i}{\text{maximum\_marks\_snapshot}_i} \times 100\right)$
- **Eligible Records:** `verification_status == 'VERIFIED'`, `maximum_marks_snapshot > 0`, non-null marks.
- **Exclusions:** Unverified records (`IMPORTED`, `CORRECTION_REQUIRED`), exempted records, cancelled tests.
- **Aggregation Level:** Student / Subject / Institution.
- **Freshness:** Updated upon faculty record verification.
- **Permitted Roles:** `STUDENT` (own), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`. (Placement Officer: BLOCKED).

#### Attendance Rate (`attendance_rate`)
- **Business Meaning:** Proportion of academic sessions attended.
- **Source Module:** Module 03 (Academic Data Intelligence Hub).
- **Source Entity:** `StudentAttendanceRecord` (`attendance_status`).
- **Calculation:** $\frac{\text{Sessions (PRESENT + LATE)}}{\text{Total Recorded Sessions}} \times 100$
- **Eligible Records:** All recorded attendance events for the student within the active academic period.
- **Permitted Roles:** `STUDENT` (own), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`.

---

### 2.2 Learning Mastery Metrics

#### Topic Mastery Percentage (`mastery_percentage`)
- **Business Meaning:** Demonstrated proficiency on a specific syllabus topic derived from rubric and question evaluations.
- **Source Module:** Module 05 (Learning Mastery & Performance Analytics).
- **Source Entity:** `TopicMasteryResult` (`mastery_percentage`, `mastery_status`).
- **Calculation:** Ratio of eligible marks obtained to total maximum marks across verified questions mapped to that topic. Returns `NULL` if evidence count $< 2$.
- **Status Classification:**
  - `DEMONSTRATED`: $\ge 70.0\%$ with sufficient evidence.
  - `DEVELOPING`: $40.0\% - 69.9\%$.
  - `NOT_DEMONSTRATED`: $< 40.0\%$.
  - `INSUFFICIENT_EVIDENCE`: Less than minimum required attempts/questions.
- **Permitted Roles:** `STUDENT` (own), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`, `PLACEMENT_OFFICER` (anonymized/aggregated competencies only).

#### CLO Attainment Rate (`clo_attainment_pct`)
- **Business Meaning:** Percentage of Course Learning Outcomes where the student achieved at least threshold attainment ($\ge 60\%$).
- **Source Module:** Module 05.
- **Source Entity:** `LearningOutcomeAttainmentResult` (`attainment_percentage`, `attainment_status`).
- **Calculation:** $\frac{\text{Count of Attained CLOs}}{\text{Total Assessed CLOs}} \times 100$

---

### 2.3 Academic Risk Prediction Metrics

#### Risk Classification (`risk_classification`)
- **Business Meaning:** Categorical risk assessment predicting semester-final academic difficulty before the cutoff date.
- **Source Module:** Module 06 (Academic Risk Prediction Engine).
- **Source Entity:** `AcademicRiskPrediction` (`risk_classification`, `risk_score`).
- **Categories:** `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `MODEL_NOT_READY`.
- **Calculation:** Trained logistic regression classifier evaluated against historical cohorts with temporal leakage validation.
- **Ethical Limitation:** Intended solely to route timely academic support. Never used for disciplinary actions or placement filtering.
- **Permitted Roles:** `STUDENT` (own explainable profile), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`.
- **FIREWALL RULE:** **STRICTLY BLOCKED FOR `PLACEMENT_OFFICER` (HTTP 403).**

---

### 2.4 Personalized Intervention Metrics

#### Active Plans Count (`active_plans_count`)
- **Business Meaning:** Number of faculty-approved academic support plans currently in progress.
- **Source Module:** Module 07 (Personalized Academic Intervention Engine).
- **Source Entity:** `AcademicInterventionPlan` (`plan_status == 'ACTIVE'`).
- **Permitted Roles:** `STUDENT` (own), `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`.
- **FIREWALL RULE:** **STRICTLY BLOCKED FOR `PLACEMENT_OFFICER` (HTTP 403).**

#### Action Completion Rate (`action_completion_rate`)
- **Business Meaning:** Proportion of assigned intervention actions completed by the student.
- **Source Module:** Module 07.
- **Source Entity:** `AcademicInterventionAction` (`action_status == 'COMPLETED'`).

---

### 2.5 Career Readiness Metrics

#### Core Competency Coverage (`core_competency_coverage`)
- **Business Meaning:** Percentage of mandatory core role requirements demonstrated at or above the required Bloom depth level.
- **Source Module:** Module 08 (Career Readiness & Industry Skill Gap Intelligence).
- **Source Entity:** `CareerReadinessAnalysis` (`core_competency_coverage`).
- **Calculation:** $\frac{\text{Demonstrated Core Requirements}}{\text{Total Core Requirements for Role}} \times 100$
- **Permitted Roles:** `STUDENT`, `FACULTY`, `PLACEMENT_OFFICER`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`.

#### Practical Evidence Coverage (`practical_evidence_coverage`)
- **Business Meaning:** Percentage of role competencies supported by faculty-verified practical projects or lab demonstrations.
- **Source Module:** Module 08.
- **Source Entity:** `CareerReadinessAnalysis` (`practical_evidence_coverage`).
- **Calculation:** $\frac{\text{Verified Project Mapped Requirements}}{\text{Total Practical Eligible Requirements}} \times 100$
- **Permitted Roles:** `STUDENT`, `FACULTY`, `PLACEMENT_OFFICER`, `INSTITUTION_ADMIN`, `SUPER_ADMIN`.
