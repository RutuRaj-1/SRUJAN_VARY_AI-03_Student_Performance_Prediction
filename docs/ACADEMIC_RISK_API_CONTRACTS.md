# Module 06: Academic Risk Prediction — API Endpoint Contracts

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 07/11  
**Module:** Academic Risk Prediction Engine

---

## 1. Overview of Endpoints

All endpoints are mounted under the base path `/api/v1/risk`.

| Method | Endpoint | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/risk/targets` | `STUDENT`, `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | List configured risk targets for tenant/subject |
| `POST` | `/api/v1/risk/targets` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Register a new academic risk target |
| `GET` | `/api/v1/risk/targets/{target_id}` | `STUDENT`, `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Retrieve target definition details |
| `GET` | `/api/v1/risk/readiness` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Audit dataset training readiness |
| `POST` | `/api/v1/risk/models/train` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Trigger model training or fallback fitting |
| `GET` | `/api/v1/risk/models` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | List registered model versions |
| `GET` | `/api/v1/risk/models/{model_version_id}` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Retrieve model hyperparameters and parameters |
| `POST` | `/api/v1/risk/models/{model_version_id}/activate` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Promote model version to active production inference |
| `POST` | `/api/v1/risk/predictions/generate` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Generate risk predictions for cohort or student |
| `GET` | `/api/v1/risk/students/{student_id}/subjects/{subject_id}/profile` | `STUDENT` (Self Only), `FACULTY`, `ADMIN` | Get student risk profile and feature explanations |
| `GET` | `/api/v1/risk/cohort/subjects/{subject_id}/summary` | `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Get aggregated cohort risk summary |

---

## 2. Request & Response Payload Examples

### 2.1 `POST /api/v1/risk/targets`
**Request Body:**
```json
{
  "subject_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
  "target_code": "MIDTERM_DEFICIT_40",
  "target_name": "Midterm Examination Critical Deficit (<40%)",
  "outcome_definition": "Student scores below 40.0% on Midterm Exam",
  "positive_label_definition": "Scores < 40.0%",
  "negative_label_definition": "Scores >= 40.0%",
  "passing_threshold_percentage": 40.0,
  "prediction_horizon_weeks": 3,
  "is_institution_policy": true
}
```
**Response (200 OK):**
```json
{
  "id": "67980312-d04b-4f67-83eb-5b0c96be8429",
  "institution_id": "4aa9cf36-26b7-4b38-8711-414e22f1c38c",
  "subject_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
  "target_code": "MIDTERM_DEFICIT_40",
  "target_name": "Midterm Examination Critical Deficit (<40%)",
  "outcome_definition": "Student scores below 40.0% on Midterm Exam",
  "positive_label_definition": "Scores < 40.0%",
  "negative_label_definition": "Scores >= 40.0%",
  "passing_threshold_percentage": 40.0,
  "prediction_horizon_weeks": 3,
  "is_institution_policy": true,
  "status": "ACTIVE",
  "created_at": "2026-11-15T13:20:00Z",
  "updated_at": "2026-11-15T13:20:00Z"
}
```

---

### 2.2 `GET /api/v1/risk/readiness?subject_id={subject_id}&target_id={target_id}`
**Response (200 OK):**
```json
{
  "institution_id": "4aa9cf36-26b7-4b38-8711-414e22f1c38c",
  "subject_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
  "target_id": "67980312-d04b-4f67-83eb-5b0c96be8429",
  "target_code": "MIDTERM_DEFICIT_40",
  "passing_threshold_percentage": 40.0,
  "total_enrolled_students": 45,
  "eligible_labeled_samples": 42,
  "positive_class_count": 9,
  "negative_class_count": 33,
  "minority_class_ratio": 0.214,
  "is_dataset_ready_for_training": true,
  "readiness_notes": [
    "Dataset satisfies minimum 20 labeled samples requirement (42 available).",
    "Positive class representation (9 samples) satisfies minimum threshold of 5."
  ],
  "recommended_model_type": "LOGISTIC_REGRESSION"
}
```

---

### 2.3 `POST /api/v1/risk/predictions/generate`
**Request Body:**
```json
{
  "subject_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
  "target_id": "67980312-d04b-4f67-83eb-5b0c96be8429",
  "target_student_id": "b1b70dfc-e092-42fe-b586-e414c5b1be70"
}
```
**Response (200 OK):**
```json
[
  {
    "id": "766a0129-cbef-4fa6-a36c-93bfb12384a2",
    "institution_id": "4aa9cf36-26b7-4b38-8711-414e22f1c38c",
    "target_id": "67980312-d04b-4f67-83eb-5b0c96be8429",
    "model_version_id": "fa217c09-4458-45a8-ba81-f09b5550daee",
    "student_id": "b1b70dfc-e092-42fe-b586-e414c5b1be70",
    "subject_id": "84bda3bb-608e-4212-9bf3-edee0692da89",
    "cutoff_date": "2026-11-15T13:25:00Z",
    "risk_score": 0.60,
    "risk_classification": "HIGH",
    "evidence_sufficiency": "STRONG",
    "prediction_status": "ACTIVE",
    "scientific_disclaimer": "Predictions reflect empirical indicators against passing thresholds, NOT student intelligence or potential.",
    "created_at": "2026-11-15T13:25:00Z",
    "explanations": [
      {
        "id": "18f673fa-f5f4-4cb4-8d48-3199c8bf21d4",
        "feature_name": "continuous_assessment_average",
        "feature_value": 36.0,
        "contribution_weight": 0.40,
        "explanation_text": "Continuous assessment average (36.0%) is critically below 40.0% threshold.",
        "source_evidence_reference": "Phase 04/05 Continuous Assessments",
        "is_adverse_factor": true
      },
      {
        "id": "2787e912-ee77-4c80-9944-e2bcfef7ebaa",
        "feature_name": "verified_attendance_percentage",
        "feature_value": 68.0,
        "contribution_weight": 0.20,
        "explanation_text": "Verified attendance rate (68.0%) falls below 75.0% institutional threshold.",
        "source_evidence_reference": "Phase 04 Attendance Ledger",
        "is_adverse_factor": true
      }
    ]
  }
]
```
