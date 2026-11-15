# Mastery Evidence Eligibility & Exclusion Framework

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 05: Learning Mastery & Performance Analytics  
**Phase:** 06/11  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  

---

## 1. Executive Purpose

A core hazard in academic analytics is **data contamination**—incorporating draft evaluations, practice attempts, unverified imported spreadsheets, or counting both question-level items and overall test totals.

The **Mastery Evidence Eligibility Engine** operates as a deterministic, auditable gatekeeper that ingests academic records and decides, with full provenance, whether each record is `INCLUDED` in the mastery calculation or `EXCLUDED` with an explicit reason code.

---

## 2. Ingestion Sources & Precedence Hierarchy

Evidence is sourced from three distinct layers of the MASTERY platform:

```
[Level 1: Highest Granularity]
Student Assessment Question Responses (student_assessment_responses)
  └── Direct topic mapping (topic_id)
  └── Direct CLO mapping (outcome_id)
  └── Direct Bloom's cognitive level mapping
        │ (Takes Precedence over Level 2 for the same attempt)
        ▼
[Level 2: Assessment Aggregates]
Student Assessment Overall Attempts (student_assessment_performances)
  └── Evaluated by faculty in Phase 05
  └── Subject-level or assessment-level evidence
        │ (Included only if Question-Level responses are absent)
        ▼
[Level 3: Institutional Gradebook]
Official Verified Academic Records (Phase 04 Academic Data Intelligence Hub)
  └── Midterm / End-Semester / Laboratory imported transcripts
  └── Verified by faculty or administrative staff
```

---

## 3. Inclusion & Exclusion Criteria Matrix

Every candidate record undergoes an eligibility audit against the following matrix:

| Criterion | Ingestion Requirement | Rejection Rationale / Exclusion Reason |
|---|---|---|
| **Verification State** | Record must have `verification_status == 'VERIFIED'` or assessment `status == 'GRADED'`. | `UNVERIFIED_DATA`: Unverified drafts or unreviewed manual submissions cannot influence mastery. |
| **Marks Integrity** | Marks possible must be $> 0$, and $0 \le \text{marks\_obtained} \le \text{marks\_possible}$. | `ZERO_MAXIMUM_MARKS` or `OUT_OF_BOUNDS_MARKS`: Prevents division-by-zero errors or fraudulent score anomalies. |
| **Practice Mode Filter** | Formal summative assessments (`QUIZ`, `MIDTERM`, `FINAL_EXAM`) are included by default. | `PRACTICE_MODE_UNSELECTED`: Formative practice quiz attempts are excluded unless faculty explicitly enables practice inclusion. |
| **Anti-Double-Counting** | Granular question records are selected over aggregate attempt totals. | `DUPLICATE_SUPERSEDED`: Total attempt performance is excluded when question-level responses have already contributed. |
| **Curriculum Linkage** | Evidence must map to a known syllabus topic or course learning outcome. | `UNMAPPED_CURRICULUM`: Assessment items with no topic/outcome mapping cannot compute topic-level mastery. |

---

## 4. The Anti-Double-Counting Guard

### The Double-Counting Vulnerability
If an exam contains 10 questions worth 10 marks each (total 100 marks), processing both the 10 individual question responses and the student's 100-mark total record would result in:
1. $200$ marks possible counted instead of $100$.
2. Artificial inflation or deflation of topic weights.
3. Skewed evidence counts ($11$ items instead of $10$).

### Algorithmic Resolution
During each analysis run:
1. The engine checks if `student_assessment_responses` exist for a given `source_attempt_id`.
2. If question-level responses exist, they are ingested as `ASSESSMENT_QUESTION` evidence records.
3. The parent `student_assessment_performances` record for that same attempt is flagged as `EXCLUDED` with `exclusion_reason = 'DUPLICATE_SUPERSEDED'`.
4. If no question-level breakdown exists (e.g., imported historical midterm marks), the aggregate `student_assessment_performances` record is ingested as `ASSESSMENT_TOTAL` or `OFFICIAL_GRADEBOOK`.

### Database Enforcement
A multi-column uniqueness constraint protects the table against race conditions:
```sql
ALTER TABLE mastery_evidence_records
ADD CONSTRAINT uq_mastery_evidence_source
UNIQUE (student_id, source_type, source_response_id, source_performance_id);
```

---

## 5. Auditability & Inspection APIs

Full transparency is exposed to faculty and students via inspection endpoints:

- `GET /api/v1/mastery/topics/{result_id}/evidence`:  
  Retrieves all contributing evidence items with raw points earned, possible, normalized percentage, weight, and Bloom's classification.

- `GET /api/v1/mastery/topics/{result_id}/excluded-evidence`:  
  Audits candidate records that were evaluated by the eligibility engine but excluded, returning the exact `exclusion_reason` (e.g., `PRACTICE_MODE_UNSELECTED`, `DUPLICATE_SUPERSEDED`).
