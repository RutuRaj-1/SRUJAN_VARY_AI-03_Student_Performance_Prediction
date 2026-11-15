# Module 06: Academic Risk Target Definitions & Horizon Policies

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 07/11  
**Module:** Academic Risk Prediction Engine

---

## 1. Problem Framing & Educational Philosophy

In traditional higher education institutions, academic "failure" is often discovered retrospectively when semester examination marks are finalized. At that late stage, corrective pedagogical interventions are impossible, resulting in course repetition, student distress, and lowered graduation rates.

MASTERY reformulates academic risk prediction as a **proactive early warning system**:
- **Target Event:** A specific, measurable academic deficit occurring at a future assessment milestone (such as a Midterm Examination, Continuous Internal Evaluation, or End-Semester Examination).
- **Time Boundary:** Predictions are evaluated at an explicit cutoff point (e.g., Week 4 or Week 8 of the semester).
- **Actionable Horizon:** The prediction horizon gives educators a window of 3–6 weeks to stage targeted learning interventions before the milestone occurs.

---

## 2. Standardized Risk Target Definitions

Institutions configure academic risk targets based on accreditation standards (e.g., NBA, NAAC, ABET) and departmental policies.

### Target 1: Midterm Examination Critical Deficit (`MIDTERM_DEFICIT_40`)
- **Target Code:** `MIDTERM_DEFICIT_40`
- **Formal Outcome Definition:** A student securing below $40.0\%$ in the Midterm Theory Examination.
- **Positive Label ($y = 1$):** Score obtained $< 40.0\%$ of maximum midterm marks.
- **Negative Label ($y = 0$):** Score obtained $\ge 40.0\%$ of maximum midterm marks.
- **Passing Threshold:** $40.0\%$
- **Prediction Horizon:** 3 weeks prior to midterm examination date.
- **Policy Intent:** Identify students struggling with introductory and foundational unit concepts before initial formal grading.

### Target 2: Continuous Internal Assessment Failure (`CIE_DEFICIT_50`)
- **Target Code:** `CIE_DEFICIT_50`
- **Formal Outcome Definition:** A student failing to attain the institutional prerequisite threshold of $50.0\%$ across aggregate continuous internal assessments (quizzes, lab evaluations, and assignments).
- **Positive Label ($y = 1$):** Cumulative continuous internal score $< 50.0\%$.
- **Negative Label ($y = 0$):** Cumulative continuous internal score $\ge 50.0\%$.
- **Passing Threshold:** $50.0\%$
- **Prediction Horizon:** Week 6 of a 14-week semester.
- **Policy Intent:** Screen students who are falling behind on routine coursework and practical lab submissions.

### Target 3: Course Final Examination Deficit (`FINAL_GRADE_DEFICIT_50`)
- **Target Code:** `FINAL_GRADE_DEFICIT_50`
- **Formal Outcome Definition:** A student securing below the university passing standard of $50.0\%$ on the Comprehensive Final Examination.
- **Positive Label ($y = 1$):** Final examination score $< 50.0\%$.
- **Negative Label ($y = 0$):** Final examination score $\ge 50.0\%$.
- **Passing Threshold:** $50.0\%$
- **Prediction Horizon:** 4–6 weeks prior to final examination commencement.
- **Policy Intent:** Allow course instructors and academic mentors sufficient time to assign personalized study plans and remedial tutoring.

---

## 3. Mathematical Formulation

Let $S$ represent a cohort of enrolled students in course subject $C$. For a target with threshold $\theta \in [0, 100]$:
$$y_i = \begin{cases} 
1 & \text{if } M_i^{\text{target}} < \theta \quad (\text{At-Risk}) \\ 
0 & \text{if } M_i^{\text{target}} \ge \theta \quad (\text{On-Track}) 
\end{cases}$$

Where $M_i^{\text{target}}$ represents the percentage marks attained by student $i$ on the target assessment milestone.

### Critical Anti-Leakage Constraint:
The actual milestone record $M_i^{\text{target}}$ is **strictly quarantined**:
$$\text{Feature Set } X_i(t_c) = \{ f(r) \mid r \in \mathcal{D}_i \land \text{timestamp}(r) \le t_c \land r \notin \mathcal{M}^{\text{target}} \}$$
Where $t_c$ is the observation cutoff date and $\mathcal{M}^{\text{target}}$ represents any record belonging to the target outcome itself.

---

## 4. Horizon Policies and Cutoff Timing

| Target Horizon | Typical Cutoff | Primary Features Consumed | Recommended Model |
| :--- | :--- | :--- | :--- |
| **Early Horizon** (Weeks 1–4) | End of Week 4 | Attendance momentum, early diagnostic quizzes | Deterministic Rule Baseline / Decision Tree |
| **Mid Horizon** (Weeks 5–8) | End of Week 8 | Midterm marks, verified lab scores, Phase 06 topic mastery | Logistic Regression / Random Forest |
| **Pre-Final Horizon** (Weeks 9–12) | End of Week 12 | Cumulative CIE average, all unit mastery profiles, learning gap severity | Calibrated Logistic Regression |

---

## 5. Non-Stigmatization Policy

MASTERY mandates that risk targets are never framed around fixed student identity:
1. Risk labels are **course-specific** and **time-bounded**. A student at risk in "Advanced Algorithms" may be excelling in "Database Engineering".
2. Labels are stored as temporary predictive warnings, not permanent academic transcripts.
3. Once the target assessment milestone has passed, the prediction is archived with actual outcome reconciliation for model calibration audits.
