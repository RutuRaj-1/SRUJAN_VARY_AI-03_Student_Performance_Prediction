# Module 06: Academic Risk Feature Engineering & Temporal Slicing

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 07/11  
**Module:** Academic Risk Prediction Engine

---

## 1. Feature Engineering Philosophy

The feature engineering pipeline transforms multi-modal academic records into a standardized, 12-dimensional numerical feature vector.

In accordance with the MASTERY digital trust charter:
- **No Demographics:** Gender, ethnicity, postal code, family income, or religion are excluded from feature vectors to prevent algorithmic bias.
- **No Invasive Telemetry:** Webcam feeds, microphone streams, biometric trackers, and continuous eye-gaze estimations are strictly barred.
- **Pure Academic Grounding:** Features represent verified curriculum mastery, historical performance trends, continuous assessment rigor, and institutional attendance compliance.

---

## 2. Standardized Feature Dictionary (12 Dimensions)

All feature values are normalized as floating-point numbers in `RiskFeatureSnapshot.feature_vector_json`:

| Feature Key | Type | Range | Description & Calculation Formula | Provenance Module |
| :--- | :--- | :--- | :--- | :--- |
| `continuous_assessment_average` | `FLOAT` | $[0.0, 100.0]$ | Mean percentage score across all verified continuous assessment records strictly preceding the cutoff date. | Phase 04 / Phase 05 |
| `assessment_score_trajectory` | `FLOAT` | $[-100.0, +100.0]$ | Linear slope or score delta between the most recent assessment and earliest assessments ($M_{\text{latest}} - M_{\text{earliest}}$). | Phase 04 Gradebook |
| `topic_mastery_ratio` | `FLOAT` | $[0.0, 1.0]$ | Ratio of syllabus topics meeting the `MASTERED` criteria over total syllabus topics in the course ($\frac{N_{\text{mastered}}}{N_{\text{total}}}$). | Phase 06 Topic Mastery |
| `needs_attention_topic_count` | `FLOAT` | $[0, \infty)$ | Total number of syllabus topics evaluated as `NEEDS_ATTENTION` ($< 50\%$ mastery with sufficient evidence). | Phase 06 Topic Mastery |
| `unassessed_topic_count` | `FLOAT` | $[0, \infty)$ | Number of syllabus topics that currently lack student assessment attempts or evidence. | Phase 06 Topic Mastery |
| `high_severity_learning_gap_count`| `FLOAT` | $[0, \infty)$ | Count of open learning gap findings classified with `HIGH` or `CRITICAL` severity (persistent misconception or prerequisite breakdown). | Phase 06 Gap Discovery |
| `total_open_learning_gaps` | `FLOAT` | $[0, \infty)$ | Cumulative count of all unresolved learning gap findings across the subject. | Phase 06 Gap Discovery |
| `learning_outcome_attainment_ratio`| `FLOAT` | $[0.0, 1.0]$ | Ratio of mapped course learning outcomes (COs) evaluated as `ATTAINED` over total syllabus outcomes. | Phase 06 Attainment |
| `verified_attendance_percentage` | `FLOAT` | $[0.0, 100.0]$ | Institutional attendance compliance rate: $\frac{\text{Present Sessions}}{\text{Total Sessions Held}} \times 100\%$. | Phase 04 Attendance |
| `attendance_momentum_slope` | `FLOAT` | $[-1.0, +1.0]$ | Rate of change in attendance rate over the preceding 3 weeks versus semester-to-date average. | Phase 04 Attendance |
| `submitted_attempts_count` | `FLOAT` | $[0, \infty)$ | Total count of official assessment attempts submitted on or before the observation cutoff date. | Phase 05 Assessments |
| `eligible_records_count` | `FLOAT` | $[0, \infty)$ | Total count of verified evidence rows contributing to the feature snapshot (evidence sufficiency anchor). | Slicing Engine |

---

## 3. Temporal Slicing & Anti-Leakage Validation

To guarantee that models are evaluated realistically without knowledge of future events, every feature query executes an explicit temporal barrier:

```python
# Temporal barrier query enforced in RiskFeatureService
records = (
    db.query(StudentAssessmentRecord)
    .join(AcademicAssessment, StudentAssessmentRecord.assessment_id == AcademicAssessment.id)
    .filter(
        StudentAssessmentRecord.student_id == student_id,
        AcademicAssessment.subject_id == subject_id,
        StudentAssessmentRecord.recorded_at <= cutoff_date,  # STRICT TEMPORAL BOUNDARY
        StudentAssessmentRecord.verification_status == "VERIFIED",
        AcademicAssessment.assessment_type != "FINAL_EXAM",  # TARGET LEAKAGE QUARANTINE
    )
    .all()
)
```

### Anti-Leakage Validator Rules:
1. **Rule TL-01 (Temporal Leakage):** If any assessment attempt or gradebook entry has `recorded_at > cutoff_date`, `TemporalLeakageError` is thrown and computation halts.
2. **Rule TL-02 (Target Leakage):** If the candidate feature matches the target assessment milestone ID, it is immediately discarded from the feature pool.
3. **Rule TL-03 (Sufficiency Gate):** If `eligible_records_count < 2`, the student is assigned `evidence_sufficiency = 'INSUFFICIENT'` and risk classification is held at `INSUFFICIENT_EVIDENCE` without imputing default failure probabilities.

---

## 4. Provenance & Audit Trail Metadata

Every snapshot records complete provenance metadata in `RiskFeatureSnapshot.data_provenance_json`:
```json
{
  "continuous_assessment_average": {
    "source": "Phase 04/05 Continuous Assessments",
    "records_examined": 4,
    "cutoff_applied": "2026-10-15T23:59:59Z"
  },
  "topic_mastery": {
    "source": "Phase 06 Topic Mastery Results",
    "total_topics": 12,
    "mastered": 5,
    "needs_attention": 3,
    "unassessed": 4
  },
  "attendance": {
    "source": "Phase 04 Attendance Ledger",
    "total_sessions": 24,
    "present_sessions": 20,
    "rate_percentage": 83.33
  }
}
```
This guarantees that any prediction can be audited, debugged, and explained back to faculty and students with complete evidentiary grounding.
