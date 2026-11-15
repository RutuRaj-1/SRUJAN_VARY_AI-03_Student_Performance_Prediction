# Module 04: Assessment Evidence Contracts

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026 (Track: AI, CyberSecurity and Digital Trust)  
**Phase:** 05/11 — Intelligent Assessment & Attentiveness Engine  
**Downstream Consumer:** Phase 06/11 — Learning Mastery & Performance Analytics Engine

---

## 1. Purpose & Architectural Boundaries

Phase 05 (Module 04) produces high-fidelity, item-level learning evidence from authentic assessment sessions and observable platform interaction telemetry.

In accordance with MASTERY's architectural boundaries:
- **Phase 05 DOES NOT calculate final mastery scores, academic risk scores, or career readiness ratings.**
- **Phase 05 guarantees atomic evidence capture, auditability, Bloom's cognitive taxonomy mapping, and observable telemetry.**
- **Phase 06 consumes these verified evidence contracts to calculate Bayesian knowledge tracing, competency progression, and performance analytics.**

---

## 2. Downstream Evidence Contracts

### Contract 1: `AssessmentAttemptEvidence`
Emitted upon attempt evaluation and verification.

```json
{
  "contract_type": "ASSESSMENT_ATTEMPT_EVIDENCE",
  "version": "1.0",
  "attempt_id": "UUID",
  "assessment_id": "UUID",
  "assessment_type": "INTERNAL_TEST | MID_TERM | QUIZ | PRACTICE_TEST",
  "student_id": "UUID",
  "institution_id": "UUID",
  "subject_id": "UUID",
  "attempt_number": 1,
  "timing": {
    "started_at": "ISO-8601",
    "submitted_at": "ISO-8601",
    "duration_seconds": 1845
  },
  "scoring": {
    "maximum_marks": 50.0,
    "marks_obtained": 42.5,
    "percentage": 85.0,
    "passed": true
  },
  "is_official_record": true,
  "items": [
    {
      "question_id": "UUID",
      "learning_outcome_id": "UUID",
      "bloom_level": "APPLY",
      "difficulty": "MEDIUM",
      "marks_allocated": 5.0,
      "marks_awarded": 5.0,
      "revision_count": 2,
      "evaluation_status": "AUTO_EVALUATED"
    }
  ]
}
```

### Contract 2: `LearningOutcomeMasteryEvidence`
Aggregates candidate performance across specific curriculum learning outcomes (`learning_outcomes.id`).

```json
{
  "contract_type": "LEARNING_OUTCOME_MASTERY_EVIDENCE",
  "outcome_id": "UUID",
  "outcome_code": "CO1",
  "bloom_level": "APPLY",
  "total_evidence_weight": 10.0,
  "score_achieved": 8.5,
  "demonstrated_ratio": 0.85,
  "item_count": 2
}
```

### Contract 3: `ObservableInteractionTelemetrySummary`
Aggregates observable behavioral traces from `learning_engagement_events`.

```json
{
  "contract_type": "OBSERVABLE_INTERACTION_TELEMETRY",
  "student_id": "UUID",
  "assessment_id": "UUID",
  "total_observable_events": 48,
  "telemetry_breakdown": {
    "ASSESSMENT_STARTED": 1,
    "ANSWER_SAVED": 15,
    "ANSWER_REVISED": 6,
    "ASSESSMENT_SUBMITTED": 1
  },
  "scientific_disclaimer": "DISCLAIMER: Learning engagement telemetry reflects observable human-computer interactions (events, timestamps, revisions). These behavioral traces must NEVER be equated with internal cognitive attention, mental concentration, or student intelligence."
}
```

---

## 3. Demarcation & Practice Test Governance

1. **Practice Tests (`PRACTICE_TEST`):**
   - Practice tests generate diagnostic evidence for student self-reflection.
   - They are **strictly barred** from writing to `student_assessment_records` and **must never affect formal GPA or official transcript gradebooks**.
2. **Official Assessments (`INTERNAL_TEST`, `MID_TERM`, `END_TERM`):**
   - Must be verified by faculty via `/submissions/{attempt_id}/release-result` before creating official records in `student_assessment_records` and generating an immutable `academic_record_audits` entry.
