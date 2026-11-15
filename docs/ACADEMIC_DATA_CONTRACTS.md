# MASTERY — Academic Data Contracts & Downstream Integration Specifications

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 03: Academic Data Intelligence Hub  
**Phase:** 04/11  
**Status:** ACTIVE SPECIFICATION & DATA CONTRACT  

---

## 1. Architectural Philosophy: Evidence vs Projection

MASTERY maintains strict boundaries between three distinct categories of information:
1. **Raw Ingested Records**: Unchecked bulk uploads stored temporarily or unverified.
2. **Verified Academic Records**: Faculty-confirmed, institutional baseline truths (Module 03).
3. **Derived Analytical Projections**: Competency mastery levels, cognitive attentiveness, risk indicators, and intervention trajectories (Modules 04, 05, 06, 08).

### Cardinal Rules for Downstream Consumers:
- **No Zero-Fill of Absences**: An absent student (`ABSENT`, `NOT_SUBMITTED`) did not demonstrate a score of 0. Modules 05 and 06 must never interpret missing assessments as poor comprehension; they must be treated as missing observations requiring attendance/engagement inquiry.
- **Provenance Transparency**: Every calculation, prediction, or intervention must cite the underlying `record_id`, `assessment_id`, and `verification_status` of the contributing evidence.
- **Separation of Concerns**: Module 03 does **not** calculate GPAs, risk scores, or competency mastery; it supplies pristine academic evidence with strict verification flags.

---

## 2. Downstream Consumption Contracts

### 2.1 Module 04: Intelligent Assessment & Attentiveness Engine (Phase 05)

**Purpose:** Connect syllabus unit learning outcomes with cognitive attentiveness and formative assessment telemetry.

#### Required Contracts from Module 03:
- **Subject Assessment Baseline:**
  ```typescript
  interface SubjectAssessmentContract {
    assessment_id: string;
    subject_id: string;
    name: string;
    assessment_type: AssessmentType;
    max_marks: number;
    weightage_percentage: number | null;
  }
  ```
- **Student Performance Snapshot:**
  ```typescript
  interface StudentPerformanceSnapshotContract {
    record_id: string;
    student_id: string;
    assessment_id: string;
    marks_obtained: number | null;
    max_marks_snapshot: number;
    percentage: number | null;
    result_status: 'PASSED' | 'FAILED' | 'ABSENT' | 'NOT_SUBMITTED' | 'EXEMPTED';
    verification_status: 'UNVERIFIED' | 'FLAGGED' | 'FACULTY_VERIFIED';
  }
  ```
- **Attentiveness Behavioral Context:**
  Attendance consistency from `student_attendance_records` provides the session engagement foundation.

---

### 2.2 Module 05: Learning Mastery & Performance Analytics (Phase 06)

**Purpose:** Map student assessment performance onto the hierarchical Bloom's taxonomy competency framework generated in Phase 03.

#### Required Contracts from Module 03:
- **Enrollment Verification:**
  Ensures that student mastery is calculated only for officially enrolled subjects in the target academic year and term (`student_subject_enrollments`).
- **Standardized Performance Evidence:**
  The mastery engine evaluates evidence by weighting verified marks (`verification_status === 'FACULTY_VERIFIED'`) higher than unverified drafts, while flagging discrepancies when marks exist without attendance records.

---

### 2.3 Module 06: Academic Risk Prediction Engine (Phase 07)

**Purpose:** Multi-horizon early warning system for academic failure, credit shortfall, or attendance debarment.

#### Required Contracts from Module 03:
- **Attendance Time-Series Aggregation:**
  ```typescript
  interface AttendanceAggregatedContract {
    student_id: string;
    subject_id: string;
    total_sessions_conducted: number;
    sessions_attended: number;
    sessions_excused: number;
    effective_attendance_percentage: number;
    trend: 'DECLINING' | 'STABLE' | 'IMPROVING';
  }
  ```
- **Formative vs Summative Trend:**
  Assessment performance trajectory across continuous internal assessments versus mid-terms.
- **Contract Boundary Constraint:**
  Missing attendance or missing assessment data triggers a `DATA_DEFICIT_WARNING` in the risk pipeline, never a false `HIGH_ACADEMIC_RISK` diagnosis.

---

### 2.4 Module 08: Personalized Academic Intervention Engine (Phase 09)

**Purpose:** Automated and faculty-guided remediation workflows.

#### Required Contracts from Module 03:
- Read access to `academic_data_quality_findings` to identify students suffering from systemic data discrepancies.
- Direct association with `academic_assessments` and `student_academic_profiles` for targeted remedial tests or re-evaluations.

---

## 3. Data Integrity & Verification Standard

| Verification Status | Meaning | Downstream Engine Handling |
|---|---|---|
| `UNVERIFIED` | Raw imported data or unapproved faculty draft | Used for provisional advisory; clearly tagged as preliminary. |
| `FLAGGED` | Failed automated validation check or contested by student | Excluded from official risk index; elevated to faculty review queue. |
| `FACULTY_VERIFIED` | Formally confirmed by authenticated faculty | Canonical evidence for official mastery calculations, risk scoring, and accreditation transcripts. |

---

## 4. REST API Ingestion and Access Surface

All operations are exposed under `/api/v1/academic-data` (and backwards-compatible `/academic` alias):
- `GET /api/v1/academic-data/overview`: High-level institutional metrics and distribution.
- `GET /api/v1/academic-data/students`: Filterable student academic directory.
- `GET /api/v1/academic-data/students/{id}`: Detailed student profile with enrollment, marks, and attendance history.
- `POST /api/v1/academic-data/assessments`: Assessment definitions.
- `POST /api/v1/academic-data/marks`: Performance mark submission with strict range checks.
- `POST /api/v1/academic-data/attendance`: Session attendance logging.
- `POST /api/v1/academic-data/imports/upload`: Multi-tenant file ingestion.
- `POST /api/v1/academic-data/imports/{id}/execute`: Safe atomic confirmation.
- `POST /api/v1/academic-data/quality/scan`: Deterministic data quality and anomaly detection scan.
- `POST /api/v1/academic-data/records/verify`: Faculty verification and auditing transition.
