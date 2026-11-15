# Learning Mastery & Performance Analytics — API Contracts

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 05: Learning Mastery & Performance Analytics  
**Phase:** 06/11  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  

---

## 1. Overview & Base Configuration

- **Base URL:** `/api/v1/mastery`
- **Authentication:** Bearer JWT required on all endpoints.
- **RBAC Matrix:**
  - `SUPER_ADMIN`: Full cross-institutional execution and retrieval.
  - `INSTITUTION_ADMIN`: Full institutional execution and retrieval.
  - `FACULTY`: Full execution and retrieval within institutional subjects.
  - `STUDENT`: Read-only access restricted strictly to self-profile and own evidence records. Forbidden from cohort summaries and analysis trigger endpoints.

---

## 2. Endpoints Specification

### 2.1. Trigger Mastery Analysis Job
Calculates or recalculates learning mastery across eligible assessment and gradebook evidence for a subject or a specific student.

- **Route:** `POST /api/v1/mastery/jobs/trigger`
- **RBAC:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
- **Request Body (`MasteryJobTriggerRequest`):**
```json
{
  "subject_id": "8f8a84b5-9371-460d-8547-062e5b985aa1",
  "target_student_id": "b3e0281b-53c7-43cf-aa0e-bc4877708552",
  "job_type": "SINGLE_STUDENT_UPDATE",
  "include_practice": false,
  "min_evidence_threshold": 2
}
```
- **Response:** `200 OK` (`MasteryJobResponse`)
```json
{
  "job_id": "f51954ca-5a02-4fc4-8833-281b0a80415a",
  "institution_id": "c1f7d1ef-2060-449e-b9f4-0b1a030ef101",
  "subject_id": "8f8a84b5-9371-460d-8547-062e5b985aa1",
  "status": "COMPLETED",
  "job_type": "SINGLE_STUDENT_UPDATE",
  "records_processed": 14,
  "evidence_included_count": 12,
  "evidence_excluded_count": 2,
  "error_details": null,
  "started_at": "2026-11-15T12:00:00Z",
  "completed_at": "2026-11-15T12:00:01Z",
  "scientific_disclaimer": "Learning mastery metrics reflect observed, normalized performance across eligible assessment items..."
}
```

---

### 2.2. Get Student Mastery Profile
Returns complete mastery analytics for a student in a subject, including demonstrated score, topic list, CLO attainment, and identified learning gaps.

- **Route:** `GET /api/v1/mastery/students/{student_id}/subjects/{subject_id}/profile`
- **RBAC:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
- **Response:** `200 OK` (`StudentMasteryProfileResponse`)
```json
{
  "student_id": "b3e0281b-53c7-43cf-aa0e-bc4877708552",
  "student_name": "Rohan Deshmukh",
  "enrollment_number": "EN-2026-CS-042",
  "subject_id": "8f8a84b5-9371-460d-8547-062e5b985aa1",
  "subject_code": "CS301",
  "subject_name": "Operating Systems",
  "overall_mastery_percentage": 82.5,
  "total_syllabus_topics_count": 8,
  "assessed_topics_count": 6,
  "mastered_topics_count": 4,
  "progressing_topics_count": 1,
  "needs_attention_topics_count": 1,
  "insufficient_evidence_topics_count": 2,
  "topic_results": [
    {
      "id": "e4a11f22-38ef-410a-8bf8-0eb1a719cf10",
      "topic_id": "t11-process-scheduling",
      "topic_name": "Process Scheduling Algorithms",
      "unit_title": "Unit 2: CPU Scheduling",
      "unit_number": 2,
      "demonstrated_percentage": 85.0,
      "raw_points_earned": 17.0,
      "raw_points_possible": 20.0,
      "evidence_count": 4,
      "distinct_assessment_types_count": 2,
      "sufficiency_level": "STRONG",
      "confidence_category": "HIGH",
      "mastery_status": "MASTERED",
      "bloom_level_distribution": {
        "REMEMBER": 100.0,
        "APPLY": 80.0
      },
      "first_evaluated_at": "2026-10-01T10:00:00Z",
      "last_evaluated_at": "2026-11-10T14:30:00Z"
    }
  ],
  "outcome_results": [
    {
      "id": "c1a01e55-14f7-4a0b-9c71-2b810f924b12",
      "outcome_id": "clo-2",
      "outcome_code": "CO2",
      "outcome_description": "Analyze CPU scheduling policies",
      "attainment_percentage": 85.0,
      "evidence_count": 4,
      "attainment_status": "ATTAINED",
      "threshold_percentage": 60.0
    }
  ],
  "learning_gaps": [
    {
      "id": "gap-901-unassessed",
      "topic_id": "t18-virtual-memory",
      "topic_name": "Virtual Memory and Paging",
      "gap_type": "UNASSESSED_CRITICAL_TOPIC",
      "severity": "HIGH",
      "observed_percentage": null,
      "description": "Topic has not been evaluated in any eligible assessment instruments.",
      "supporting_evidence": { "assessed_items_count": 0 }
    }
  ],
  "scientific_disclaimer": "Learning mastery metrics reflect observed, normalized performance..."
}
```

---

### 2.3. Get Cohort Mastery Summary
Provides aggregated subject analytics across all enrolled students in a cohort, calculating curriculum coverage percentage and topic performance distribution.

- **Route:** `GET /api/v1/mastery/cohort/subjects/{subject_id}/summary`
- **RBAC:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`
- **Response:** `200 OK` (`CohortMasterySummaryResponse`)
```json
{
  "subject_id": "8f8a84b5-9371-460d-8547-062e5b985aa1",
  "subject_code": "CS301",
  "subject_name": "Operating Systems",
  "total_students_enrolled": 60,
  "students_analyzed": 58,
  "curriculum_coverage_percentage": 75.0,
  "topic_aggregates": [
    {
      "topic_id": "t11-process-scheduling",
      "topic_name": "Process Scheduling Algorithms",
      "assessed_candidates_count": 58,
      "average_mastery_percentage": 78.4,
      "has_sufficient_evidence": true
    }
  ],
  "scientific_disclaimer": "Learning mastery metrics reflect observed..."
}
```

---

### 2.4. Get Longitudinal Performance Trends
Computes chronological mastery progression across assessments over time, paired with a cognitive radar across Bloom's Taxonomy levels.

- **Route:** `GET /api/v1/mastery/students/{student_id}/subjects/{subject_id}/trends`
- **RBAC:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
- **Response:** `200 OK` (`StudentPerformanceTrendsResponse`)
```json
{
  "student_id": "b3e0281b-53c7-43cf-aa0e-bc4877708552",
  "subject_id": "8f8a84b5-9371-460d-8547-062e5b985aa1",
  "timeline_points": [
    {
      "date": "2026-10-01",
      "assessment_title": "Midterm Examination 1",
      "assessment_type": "MIDTERM",
      "percentage": 76.5,
      "topics_covered_count": 3
    },
    {
      "date": "2026-11-10",
      "assessment_title": "Quiz 2: Scheduling",
      "assessment_type": "QUIZ",
      "percentage": 85.0,
      "topics_covered_count": 1
    }
  ],
  "cognitive_radar": {
    "REMEMBER": 92.0,
    "UNDERSTAND": 84.0,
    "APPLY": 78.5,
    "ANALYZE": 70.0,
    "EVALUATE": null,
    "CREATE": null
  },
  "scientific_disclaimer": "Learning mastery metrics reflect observed..."
}
```

---

### 2.5. Evidence Traceability & Inspection
Inspects the individual raw records supporting or excluded from a specific topic mastery result.

- **Route:** `GET /api/v1/mastery/topics/{result_id}/evidence`
- **Route:** `GET /api/v1/mastery/topics/{result_id}/excluded-evidence`
- **RBAC:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `FACULTY`, `STUDENT` (Self only)
- **Response:** `200 OK` (`List[MasteryEvidenceItemResponse]`)
```json
[
  {
    "id": "ev-01",
    "source_type": "ASSESSMENT_QUESTION",
    "assessment_type": "QUIZ",
    "marks_obtained": 4.5,
    "marks_possible": 5.0,
    "normalized_percentage": 90.0,
    "weight": 1.0,
    "bloom_level": "APPLY",
    "eligibility_status": "INCLUDED",
    "exclusion_reason": null,
    "attempt_timestamp": "2026-10-15T11:20:00Z"
  }
]
```
