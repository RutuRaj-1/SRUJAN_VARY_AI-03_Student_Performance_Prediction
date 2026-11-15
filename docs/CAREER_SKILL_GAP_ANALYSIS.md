# MASTERY — Industry Skill Gap Analysis
## Categorization Taxonomy and Prioritization Logic

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 08 — Career Readiness & Industry Skill Gap Intelligence  

---

## 1. Skill Gap Taxonomy

Traditional platforms reduce skill gaps to a generic "Missing Skill" indicator. MASTERY recognizes five distinct root causes:

| Gap Type | Description | Remedial Remedy |
|---|---|---|
| **`DEMONSTRATED_GAP`** | The student completed evaluations, but observed performance fell below the benchmark depth. | Targeted problem sets, revision labs, or reassessment attempts. |
| **`EVIDENCE_GAP`** | The competency is required, but the student has not yet completed suitable assessments or submissions (`NOT_ASSESSED`). | Scheduling assessment opportunities or micro-evaluations. |
| **`CURRICULUM_GAP`** | The university curriculum does not provide an academic learning pathway or subject for this industry competency. | Independent extracurricular projects, online modules, or workshop enrollments. |
| **`PRACTICAL_EVIDENCE_GAP`** | The student demonstrated strong theoretical knowledge in exams ($\ge 70\%$), but lacks verified code, laboratory, or repository evidence. | Building and submitting a practical project for faculty review. |
| **`MAPPING_GAP`** | An industry requirement is suggested by AI or newly introduced, but has not yet received department faculty review. | Faculty curriculum committee review and validation. |

---

## 2. Gap Severity Prioritization

Gaps are prioritized deterministically:

1. **`CRITICAL`:** Core competency deficit with `DEMONSTRATED_GAP` where prerequisites are also missing.
2. **`HIGH`:** Core competency deficit (`CORE` or `HIGH` importance) or practical gap in primary role domain.
3. **`MODERATE`:** Supporting competency gap or developing state in an important competency.
4. **`LOW`:** Optional competency gap, informational note, or pending mapping review.

---

## 3. Explanatory Structure of a Skill Gap Record

Every discovered gap record in `career_skill_gap_findings` maintains four explanatory dimensions:

```json
{
  "competency_name": "Relational & NoSQL Database Design",
  "gap_type": "PRACTICAL_EVIDENCE_GAP",
  "gap_severity": "MODERATE",
  "rationale": "Demonstrated conceptual mastery in academic assessments, but lacks verified practical code or project evidence.",
  "suggested_action": "Build a hands-on project demonstrating Relational & NoSQL Database Design and submit for faculty review.",
  "evidence_needed": "Verified repository or lab submission."
}
```
