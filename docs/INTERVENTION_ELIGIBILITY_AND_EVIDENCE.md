# Module 07: Intervention Eligibility, Evidence Provenance & Anti-Leakage

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 08/11  
**Module:** 07 — Personalized Academic Intervention Engine  

---

## 1. Evidence Eligibility Rules

To preserve student digital trust and institutional credibility, recommendations and intervention plans must only consume eligible evidence.

### 1.1 Eligible Evidence Sources
1. **Verified Continuous Assessments (Phase 04):** Midterm exams, lab tests, and class quizzes marked with `verification_status == 'VERIFIED'`.
2. **Online Assessment Attempts (Phase 05):** Official test attempts submitted within scheduled windows and evaluated by faculty rubrics (`status == 'EVALUATED'`). Practice tests (`assessment_type == 'PRACTICE_TEST'`) are excluded.
3. **Calibrated Topic Mastery (Phase 06):** Topic mastery percentages calculated under the deterministic weighting algorithm with statistical sufficiency $\ge \text{'MODERATE'}$.
4. **Learning Gap Findings (Phase 06):** Formally identified curriculum vulnerability records with `status == 'OPEN'`.
5. **Time-Bounded Risk Signals (Phase 07):** Predictions generated with cutoff dates preceding future milestone horizons.

### 1.2 Ineligible & Barred Evidence
- **Raw Telemetry as Deficit Proof:** Tab-switch counts, idle time durations, mouse trajectories, or answer revision frequencies are **strictly barred** from serving as justification for an intervention.
- **Biometric Surveillance:** Webcam video streams, audio recordings, or eye-gaze tracking are forbidden under the MASTERY digital trust charter.
- **Unverified / Draft Gradebooks:** Any assessment record marked as `DRAFT` or `UNVERIFIED` is ignored by the recommendation engine.
- **Demographic Attributes:** Gender, socioeconomic status, ethnicity, or hometown cannot influence eligibility or priority.

---

## 2. Evidence Provenance Tracing

Every recommendation records explicit provenance metadata in `source_evidence_summary`:

```json
{
  "gap_id": "81e15e10-baea-45d6-959f-158b0f6b8c4e",
  "finding_type": "PERSISTENT_LOW_SCORE",
  "severity": "HIGH",
  "evidence_summary": "Continuous score deficit on Paxos Consensus (<40% across 2 midterms)",
  "supporting_evidence_refs": {
    "assessment_record_ids": [
      "18f673fa-f5f4-4cb4-8d48-3199c8bf21d4",
      "2787e912-ee77-4c80-9944-e2bcfef7ebaa"
    ],
    "cutoff_applied": "2026-10-15T23:59:59Z"
  }
}
```

This provenance allows both faculty advisors and students to verify exactly which assessments or test items contributed to the recommendation.

---

## 3. Temporal Cutoff & Anti-Leakage Integration

Interventions inherit the strict temporal boundaries established in Phase 07:
- When an intervention is triggered from a Phase 07 risk prediction, it operates on feature evidence recorded strictly on or before the prediction cutoff date (`recorded_at <= prediction_cutoff_date`).
- Future assessment outcomes cannot be referenced in current intervention recommendations.
- Subsequent post-intervention assessments are quarantined for observational outcome tracking in `intervention_outcome_observations`.
