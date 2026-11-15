# Module 06: Academic Risk Explainability, Grounded Attributions & Ethical Governance

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 07/11  
**Module:** Academic Risk Prediction Engine

---

## 1. The Imperative for Grounded Explainability

In educational technology, black-box predictions produce confusion and distrust. When a student or instructor is shown a score of "78% Risk" without clear explanation:
- The faculty member does not know what topic or behavior to intervene on.
- The student feels labeled, anxious, and helpless.
- Academic advisors cannot verify whether the risk is caused by genuine conceptual struggle, missing assignments, or an administrative recording error.

MASTERY mandates **Grounded Explainability**: every risk score must be decomposed into explicit, verified evidentiary factors stored in `academic_risk_prediction_explanations`.

---

## 2. Feature Attribution Engine

### 2.1 Logistic Regression Attribution
For linear models, attribution weights are derived directly from standardized inputs:
$$\phi_j = w_j \cdot \left( \frac{x_j - \mu_j}{\sigma_j} \right)$$
- If $\phi_j > 0$: The feature increases risk of deficit $\rightarrow$ Flagged as **Adverse Risk Factor** (`is_adverse_factor = True`).
- If $\phi_j < 0$: The feature decreases risk of deficit $\rightarrow$ Flagged as **Protective Factor** (`is_adverse_factor = False`).

### 2.2 Deterministic Rule Baseline Attribution
When deterministic rules are evaluated, each triggered rule contributes a concrete evidentiary explanation:

| Trigger Condition | Contribution Weight | Generated Explanation Text | Source Provenance | Adverse? |
| :--- | :--- | :--- | :--- | :--- |
| $\text{Continuous Avg} < 40.0\%$ | $+0.40$ | "Continuous assessment average (36.0%) is critically below 40.0% threshold." | Phase 04/05 Continuous Assessments | Yes |
| $\text{Continuous Avg} \ge 70.0\%$ | $-0.30$ | "Continuous assessment average (78.5%) demonstrates strong conceptual foundation." | Phase 04/05 Continuous Assessments | No |
| $\text{High Severity Gaps} \ge 2$ | $+0.30$ | "2 unresolved high-severity topic gaps identified in curriculum." | Phase 06 Learning Gap Findings | Yes |
| $\text{Verified Attendance} < 75.0\%$ | $+0.20$ | "Verified attendance rate (68.0%) falls below 75.0% institutional threshold." | Phase 04 Attendance Ledger | Yes |
| $\text{Unassessed Topics} \ge 3$ | $+0.10$ | "3 syllabus topics currently lack assessment evaluation." | Phase 06 Topic Mastery | Yes |

---

## 3. Human-in-the-Loop Advisory Principles

1. **Non-Automated Adverse Decisions:** Predictions are intended solely for **advising and supportive intervention**. No academic expulsion, grade penalty, or financial aid cancellation can be made automatically based on risk scores.
2. **Student Inspection Right:** Students have the affirmative right to inspect all contributing factors and evidence provenance for their predictions.
3. **Evidence Challenge Workflow:** If a student identifies that an attendance record was recorded incorrectly, fixing the attendance record automatically recalculates the feature snapshot and risk attribution.

---

## 4. Placement Officer Firewall (§ 4.2 Ethical AI Charter)

To ensure student digital trust and prevent systemic employment bias:
- **Placement Officers are strictly barred** from viewing student academic risk scores, risk classifications, or predictive early warning logs.
- Career readiness modules (Phase 09) consume verified competency attainment and skill demonstrations, **never** early-semester predictive risk probabilities.
- System enforcement is applied at database level via Supabase RLS and application level via FastAPI security guards (`require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])`).
