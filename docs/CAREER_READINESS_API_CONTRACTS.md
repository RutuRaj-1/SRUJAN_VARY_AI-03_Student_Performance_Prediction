# MASTERY — Career Readiness API Contracts
## REST API Endpoint Specifications for Module 08

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 08 — Career Readiness & Industry Skill Gap Intelligence  
**Base URL:** `/api/v1/career-readiness`  

---

## 1. Endpoints Overview

| Method | Endpoint | Authorization | Description |
|---|---|---|---|
| `GET` | `/roles` | Authenticated | List all active career role benchmarks |
| `GET` | `/roles/{role_id}` | Authenticated | Retrieve details and requirements of a role |
| `POST` | `/roles` | Staff (Admin/Faculty) | Create a new custom or institutional role |
| `PUT` | `/roles/{role_id}` | Staff (Admin/Faculty) | Update role properties or review status |
| `POST` | `/roles/{role_id}/requirements` | Staff (Admin/Faculty) | Add a competency requirement to a role |
| `GET` | `/projects` | Authenticated | List submitted student practical projects |
| `POST` | `/projects` | Student / Staff | Submit practical project evidence |
| `PUT` | `/projects/{project_id}` | Student Owner | Edit project evidence (prior to review) |
| `POST` | `/projects/{project_id}/review` | Faculty / Admin | Review and verify student project evidence |
| `GET` | `/evidence` | Authenticated | Retrieve student competency evidence ledger |
| `POST` | `/analyze` | Authenticated | Run/retrieve role readiness analysis |
| `GET` | `/compare` | Authenticated | Compare multiple roles side-by-side |
| `GET` | `/overview` | Authenticated | Aggregate career readiness workspace metrics |
| `GET` | `/recommendations` | Authenticated | List development recommendations |
| `PATCH`| `/recommendations/{id}` | Authenticated | Update recommendation status or notes |

---

## 2. Key Payload Schemas

### `POST /api/v1/career-readiness/analyze`
**Request:**
```json
{
  "role_id": "b4dc2233-3446-4afc-8358-49fb17b2b343",
  "student_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "force_recalculate": false
}
```

**Response (200 OK):**
```json
{
  "id": "e4b1c2d3-1234-5678-9abc-def012345678",
  "institution_id": "11111111-1111-1111-1111-111111111111",
  "student_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "role_id": "b4dc2233-3446-4afc-8358-49fb17b2b343",
  "role_title": "Software Development Engineer - Backend",
  "alignment_status": "STRONG_EVIDENCE_ALIGNMENT",
  "total_requirements_count": 6,
  "demonstrated_count": 4,
  "developing_count": 1,
  "insufficient_evidence_count": 0,
  "not_assessed_count": 1,
  "review_required_count": 0,
  "core_competency_coverage": 80.0,
  "practical_evidence_coverage": 66.7,
  "faculty_reviewed_count": 3,
  "summary_rationale": "Student demonstrates strong evidence alignment (80.0% core coverage, 66.7% practical coverage) across Software Development Engineer - Backend requirements.",
  "disclaimer": "Career readiness evaluations reflect observed alignment between demonstrated academic, assessment, and verified practical project evidence against curated industry role competency profiles...",
  "analysis_version": "v1.0-deterministic",
  "created_at": "2026-11-15T15:20:00Z",
  "gap_findings": [],
  "recommendations": []
}
```
