# MASTERY — Data Freshness, Snapshots & Provenance
## Temporal Semantics across Aggregated Intelligence

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 10/11 — Unified Intelligence Dashboard & Cross-Module Integration  

---

## 1. Freshness Architecture

Every aggregated response and component card in MASTERY carries a typed `DataFreshnessInfo` schema:
```json
{
  "last_updated_at": "2026-11-15T14:30:00Z",
  "source_module": "Module 05: Learning Mastery & Performance Analytics",
  "freshness_status": "FRESH",
  "is_snapshot": true,
  "details": "Calibrated over 18 topics and 6 Course Learning Outcomes."
}
```

### 1.1 Freshness Classification
- `FRESH`: Data was calculated or updated within the current active session or within the last 24 hours.
- `RECENT`: Stored snapshot calculated within the last 7 days; reflects valid semester state.
- `STALE`: Source assessment or attendance records have updated since the snapshot was generated; re-calculation recommended.
- `NOT_AVAILABLE`: No baseline evaluation or screening exists on record.

---

## 2. Dynamic vs Snapshot Semantics

| Intelligence Dimension | Mode | Underlying Table | Rationale |
|---|---|---|---|
| **Academic Records** | Dynamic Query | `StudentAssessmentRecord`, `StudentAttendanceRecord` | Live institutional ledger; recalculates verified averages upon each query. |
| **Topic Mastery** | Immutable Snapshot | `TopicMasteryResult` | Calibrated via deterministic `MasteryAnalysisJob`; changes only when a new calibration job runs. |
| **Academic Risk** | Time-Bounded Snapshot | `AcademicRiskPrediction` | Validated against temporal leakage at a specific historical cutoff date. Never dynamically recomputed on arbitrary dates. |
| **Interventions** | Dynamic Workflow | `AcademicInterventionPlan`, `AcademicInterventionAction` | Reflects live faculty reviews, mentor comments, and student action completions. |
| **Career Readiness** | Deterministic Snapshot | `CareerReadinessAnalysis` | Generated from snapshot multi-modal evidence matching industry role frameworks. |

---

## 3. Provenance & Non-Destructive Null Handling

### Rule 1: No Conversion of Missing Evidence into Zero
If a student has not taken assessments for a topic, `TopicMasteryResult.mastery_percentage` remains `NULL` and `mastery_status` is `INSUFFICIENT_EVIDENCE`. The dashboard displays `"Pending Evidence"`, never `0.0%`.

### Rule 2: Source Module Attribution
Every card on the unified dashboard displays a provenance pill specifying the source module (e.g. `Module 03`, `Module 05`, `Module 06`, `Module 08`) with direct deep-links to the full module workspace for deep inspection.
