# MASTERY — Dashboard API Contracts
## OpenAPI Specifications for Phase 10 Endpoints

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 10/11 — Unified Intelligence Dashboard & Cross-Module Integration  

---

## 1. Student Intelligence Dashboard

### `GET /api/v1/dashboard/student/overview`
Aggregates profile header, academic records, mastery, explainable risk, interventions, and career readiness.

**Query Parameters:**
- `student_id` (optional, UUID): Target student profile ID (authorized for faculty/admins).

**Response (200 OK):**
```json
{
  "student_profile": {
    "id": "0aa22017-62cc-4586-8929-68c77877aa3e",
    "full_name": "Aarav Sharma",
    "enrollment_number": "APEX-CSE-2023-001",
    "program_name": "B.Tech Computer Science and Engineering",
    "department": "Computer Science & Engineering",
    "current_semester": 5,
    "institution_name": "Apex Institute of Technology",
    "academic_status": "ENROLLED"
  },
  "academic_performance": {
    "average_marks": 84.0,
    "attendance_rate": 92.5,
    "total_records": 12,
    "verified_records_count": 10,
    "pending_records_count": 2,
    "enrolled_subjects_count": 6,
    "freshness": {
      "last_updated_at": "2026-11-15T15:30:00Z",
      "source_module": "Module 03: Academic Data Intelligence Hub",
      "freshness_status": "FRESH",
      "is_snapshot": false
    }
  },
  "mastery_summary": {
    "topics_assessed_count": 18,
    "topics_demonstrated_count": 14,
    "topics_developing_count": 3,
    "topics_insufficient_evidence_count": 1,
    "clo_attainment_pct": 78.5,
    "active_learning_gaps_count": 2,
    "freshness": {
      "last_updated_at": "2026-11-15T14:00:00Z",
      "source_module": "Module 05: Learning Mastery & Performance Analytics",
      "freshness_status": "FRESH",
      "is_snapshot": true
    }
  },
  "risk_summary": {
    "has_prediction": true,
    "risk_classification": "LOW",
    "risk_probability": 0.18,
    "prediction_horizon": "End of Current Semester Examination",
    "primary_adverse_factors": ["Mid-term 1 score below median in Advanced Data Structures"],
    "protective_factors": ["High attendance (92.5%)", "Consistent continuous lab assignment submissions"],
    "prediction_timestamp": "2026-11-10T00:00:00Z",
    "model_version": "v1.0-LogisticRegression",
    "disclaimer": "Academic risk predictions indicate potential difficulty under observed conditions, not guaranteed academic failure.",
    "freshness": {
      "last_updated_at": "2026-11-10T00:00:00Z",
      "source_module": "Module 06: Academic Risk Prediction Engine",
      "freshness_status": "FRESH",
      "is_snapshot": true
    }
  },
  "intervention_summary": {
    "active_plans_count": 1,
    "pending_actions_count": 2,
    "completed_actions_count": 3,
    "latest_plan_title": "Algorithm Refinement & Problem Solving Support",
    "faculty_mentor_name": "Dr. Alan Turing",
    "freshness": {
      "last_updated_at": "2026-11-14T10:15:00Z",
      "source_module": "Module 07: Personalized Academic Intervention Engine",
      "freshness_status": "FRESH",
      "is_snapshot": false
    }
  },
  "career_summary": {
    "analyzed_roles_count": 2,
    "target_role_title": "Backend Systems Engineer",
    "core_coverage_pct": 75.0,
    "practical_coverage_pct": 60.0,
    "alignment_status": "PARTIAL_EVIDENCE_ALIGNMENT",
    "verified_projects_count": 1,
    "pending_projects_count": 1,
    "active_skill_gaps_count": 2,
    "freshness": {
      "last_updated_at": "2026-11-15T12:00:00Z",
      "source_module": "Module 08: Career Readiness & Industry Skill Gap Intelligence",
      "freshness_status": "FRESH",
      "is_snapshot": true
    }
  },
  "system_freshness": "2026-11-15T16:00:00Z"
}
```

---

## 2. Faculty Dashboard

### `GET /api/v1/dashboard/faculty/overview`
Aggregates assigned subjects, verification queues, and cohort risk flags.

**Response (200 OK):**
```json
{
  "faculty_name": "Dr. Alan Turing",
  "institution_name": "Apex Institute of Technology",
  "department": "Computer Science & Engineering",
  "assigned_subjects": [
    {
      "subject_id": "4c150a2c-b42d-4704-b884-aebfa7cee086",
      "code": "CS301",
      "name": "Advanced Data Structures",
      "semester": 5,
      "enrolled_students_count": 64,
      "average_attendance": 88.4,
      "average_marks": 74.2
    }
  ],
  "total_students_monitored": 64,
  "verification_queue": {
    "pending_academic_records": 14,
    "pending_interventions_review": 3,
    "pending_practical_projects": 5
  },
  "cohort_risk_overview": {
    "high_risk_students_count": 4,
    "moderate_risk_students_count": 9,
    "low_risk_students_count": 51,
    "learning_gaps_flagged_count": 12,
    "active_interventions_count": 7
  },
  "freshness": {
    "last_updated_at": "2026-11-15T16:00:00Z",
    "source_module": "Unified Dashboard Integration Layer",
    "freshness_status": "FRESH",
    "is_snapshot": false
  }
}
```

---

## 3. Placement Officer Dashboard

### `GET /api/v1/dashboard/placement/overview`
Career framework alignments and practical project ledger. Strictly firewalled from risk and interventions.

**Response (200 OK):**
```json
{
  "institution_name": "Apex Institute of Technology",
  "active_role_profiles_count": 5,
  "total_evaluated_students": 120,
  "readiness_distribution": {
    "ready_count": 28,
    "approaching_count": 45,
    "developing_count": 32,
    "emerging_or_unassessed_count": 15
  },
  "project_verification_summary": {
    "verified_projects_count": 86,
    "pending_verification_count": 14
  },
  "top_industry_skill_gaps": [
    {
      "competency_name": "Distributed Consensus",
      "gap_type": "PRACTICAL_EVIDENCE_GAP",
      "affected_students_count": 34
    },
    {
      "competency_name": "Cloud Native Observability",
      "gap_type": "CURRICULUM_GAP",
      "affected_students_count": 29
    }
  ],
  "freshness": {
    "last_updated_at": "2026-11-15T16:00:00Z",
    "source_module": "Module 08: Career Readiness & Industry Skill Gap Intelligence",
    "freshness_status": "FRESH",
    "is_snapshot": false,
    "details": "Firewalled career readiness intelligence. Academic risk and intervention data are excluded by design."
  }
}
```
