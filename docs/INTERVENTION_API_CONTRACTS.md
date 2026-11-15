# Module 07: Academic Interventions — API Contracts & Payload Specifications

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 08/11  
**Module:** 07 — Personalized Academic Intervention Engine  

---

## 1. Endpoint Index

Base URL: `/api/v1/interventions`

| Method | Endpoint | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/interventions/templates` | `STUDENT`, `FACULTY`, `ADMIN` | List approved intervention templates |
| `POST` | `/api/v1/interventions/templates` | `FACULTY`, `ADMIN` | Create a new template blueprint |
| `POST` | `/api/v1/interventions/recommendations/generate` | `FACULTY`, `ADMIN` | Generate evidence-grounded recommendations |
| `GET` | `/api/v1/interventions/recommendations` | `STUDENT` (Self), `FACULTY`, `ADMIN` | List recommendations |
| `POST` | `/api/v1/interventions/plans` | `FACULTY`, `ADMIN` | Author a new intervention plan |
| `GET` | `/api/v1/interventions/plans` | `STUDENT` (Self), `FACULTY`, `ADMIN` | List intervention plans |
| `GET` | `/api/v1/interventions/plans/{plan_id}` | `STUDENT` (Self), `FACULTY`, `ADMIN` | Retrieve full plan details, actions, and progress |
| `POST` | `/api/v1/interventions/plans/{plan_id}/review` | `FACULTY`, `ADMIN` | Faculty approval or rejection checkpoint |
| `POST` | `/api/v1/interventions/plans/{plan_id}/assign` | `FACULTY`, `ADMIN` | Assign approved plan to student dashboard |
| `POST` | `/api/v1/interventions/actions/{action_id}/status` | `STUDENT`, `FACULTY`, `ADMIN` | Update action state (Start, Submit, Verify) |
| `POST` | `/api/v1/interventions/plans/{plan_id}/outcomes` | `FACULTY`, `ADMIN` | Record post-intervention outcome observation |
| `GET` | `/api/v1/interventions/plans/{plan_id}/outcomes` | `STUDENT` (Self), `FACULTY`, `ADMIN` | List outcome observations for plan |
| `GET` | `/api/v1/interventions/dashboard/faculty` | `FACULTY`, `ADMIN` | Faculty intervention dashboard metrics |
| `GET` | `/api/v1/interventions/dashboard/student` | `STUDENT` | Student assigned action workspace |

---

## 2. Sample Payloads

### 2.1 `POST /api/v1/interventions/plans`
**Request Body:**
```json
{
  "student_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
  "subject_id": "4aa9cf36-26b7-4b38-8711-414e22f1c38c",
  "topic_id": "b1b70dfc-e092-42fe-b586-e414c5b1be70",
  "plan_title": "Paxos Consensus Mastery Acceleration",
  "learning_objective": "Attain minimum 70% demonstrated understanding on Paxos algorithmic phases.",
  "target_completion_date": "2026-11-25T23:59:59Z",
  "expected_outcome_evidence": "Verification quiz submission and lab practice logs",
  "initial_actions": [
    {
      "action_title": "Review Multi-Paxos Phase 1 & 2 Invariants",
      "action_type": "TARGETED_REVISION",
      "instructions": "Study Lamport's original paper notes and review lecture slides on quorum intersection.",
      "estimated_effort_hours": 2.0
    },
    {
      "action_title": "Implement Leader Election Simulation in Python",
      "action_type": "LAB_PRACTICE",
      "instructions": "Build consensus test harness simulating split-brain network partition scenarios.",
      "estimated_effort_hours": 3.5
    }
  ]
}
```

### 2.2 `POST /api/v1/interventions/actions/{action_id}/status`
**Student Submission Request:**
```json
{
  "new_status": "SUBMITTED",
  "student_completion_notes": "Implemented Python simulation with 5 nodes; verified leader consensus across simulated drop rates.",
  "student_submission_url": "https://github.com/ait-cs/paxos-lab-solution"
}
```

**Faculty Verification Request:**
```json
{
  "new_status": "VERIFIED",
  "faculty_feedback": "Verified test cases. Node partition handling correctly preserved safety invariants."
}
```
