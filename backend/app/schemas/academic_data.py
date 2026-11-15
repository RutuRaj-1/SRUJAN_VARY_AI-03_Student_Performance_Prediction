import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import (
    AssessmentType,
    AssessmentResultStatus,
    AttendanceStatus,
    RecordVerificationStatus,
    DataQualitySeverity,
    ImportCategory,
    ImportJobStatus,
)


# --- Student Academic Profile Schemas ---

class StudentAcademicProfileBase(BaseModel):
    enrollment_number: str = Field(..., json_schema_extra={"example": "2022-CSE-042"})
    admission_number: Optional[str] = Field(None, json_schema_extra={"example": "ADM-2022-042"})
    first_name: str = Field(..., json_schema_extra={"example": "Aarav"})
    last_name: str = Field(..., json_schema_extra={"example": "Patel"})
    email: Optional[str] = Field(None, json_schema_extra={"example": "aarav.patel@ait.edu"})
    department: str = Field(default="Computer Science & Engineering", json_schema_extra={"example": "Computer Science & Engineering"})
    admission_year: int = Field(default=2022, ge=2000, le=2100)
    current_semester: int = Field(default=4, ge=1, le=12)
    academic_status: str = Field(default="ENROLLED", json_schema_extra={"example": "ENROLLED"})


class StudentAcademicProfileCreate(StudentAcademicProfileBase):
    institution_id: uuid.UUID
    program_id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None


class StudentAcademicProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    current_semester: Optional[int] = None
    academic_status: Optional[str] = None
    program_id: Optional[uuid.UUID] = None
    profile_id: Optional[uuid.UUID] = None


class StudentAcademicProfileResponse(StudentAcademicProfileBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    program_id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    program_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Student Subject Enrollment Schemas ---

class StudentSubjectEnrollmentBase(BaseModel):
    academic_year: str = Field(default="2024-2025", json_schema_extra={"example": "2024-2025"})
    semester: int = Field(..., ge=1, le=12, json_schema_extra={"example": 4})
    enrollment_status: str = Field(default="ACTIVE", json_schema_extra={"example": "ACTIVE"})


class StudentSubjectEnrollmentCreate(StudentSubjectEnrollmentBase):
    institution_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID


class StudentSubjectEnrollmentResponse(StudentSubjectEnrollmentBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    student_name: Optional[str] = None
    enrollment_number: Optional[str] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    enrolled_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Academic Assessment Schemas ---

class AcademicAssessmentBase(BaseModel):
    assessment_name: str = Field(..., json_schema_extra={"example": "Internal Test 1"})
    assessment_type: AssessmentType = AssessmentType.INTERNAL_TEST
    academic_year: str = Field(default="2024-2025", json_schema_extra={"example": "2024-2025"})
    semester: int = Field(..., ge=1, le=12, json_schema_extra={"example": 4})
    maximum_marks: float = Field(..., gt=0, json_schema_extra={"example": 50.0})
    passing_marks: Optional[float] = Field(None, ge=0, json_schema_extra={"example": 20.0})
    weightage_percentage: Optional[float] = Field(None, ge=0, le=100, json_schema_extra={"example": 20.0})
    assessment_date: Optional[datetime] = None
    description: Optional[str] = None
    status: str = Field(default="SCHEDULED", json_schema_extra={"example": "SCHEDULED"})


class AcademicAssessmentCreate(AcademicAssessmentBase):
    institution_id: uuid.UUID
    subject_id: uuid.UUID


class AcademicAssessmentResponse(AcademicAssessmentBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    subject_id: uuid.UUID
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Student Performance Records Schemas ---

class StudentAssessmentRecordBase(BaseModel):
    marks_obtained: Optional[float] = Field(None, ge=0, json_schema_extra={"example": 42.5})
    result_status: AssessmentResultStatus = AssessmentResultStatus.PASSED
    remarks: Optional[str] = None


class StudentAssessmentRecordCreate(StudentAssessmentRecordBase):
    institution_id: uuid.UUID
    student_id: uuid.UUID
    assessment_id: uuid.UUID
    source_type: str = "MANUAL"
    verification_status: RecordVerificationStatus = RecordVerificationStatus.IMPORTED
    source_reference: Optional[str] = None


class StudentAssessmentRecordResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    enrollment_number: Optional[str] = None
    assessment_id: uuid.UUID
    assessment_name: Optional[str] = None
    assessment_type: Optional[AssessmentType] = None
    subject_id: Optional[uuid.UUID] = None
    subject_code: Optional[str] = None
    marks_obtained: Optional[float] = None
    maximum_marks_snapshot: float
    result_status: AssessmentResultStatus
    source_type: str
    verification_status: RecordVerificationStatus
    recorded_by: Optional[uuid.UUID] = None
    verified_by: Optional[uuid.UUID] = None
    recorded_at: datetime
    verified_at: Optional[datetime] = None
    source_reference: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Attendance Records Schemas ---

class StudentAttendanceRecordBase(BaseModel):
    academic_year: str = Field(default="2024-2025", json_schema_extra={"example": "2024-2025"})
    semester: int = Field(..., ge=1, le=12, json_schema_extra={"example": 4})
    attendance_date: datetime
    session_name: str = Field(default="Regular Session", json_schema_extra={"example": "Lecture 12"})
    attendance_status: AttendanceStatus = AttendanceStatus.PRESENT


class StudentAttendanceRecordCreate(StudentAttendanceRecordBase):
    institution_id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    source_type: str = "MANUAL"
    verification_status: RecordVerificationStatus = RecordVerificationStatus.IMPORTED
    source_reference: Optional[str] = None


class StudentAttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    enrollment_number: Optional[str] = None
    subject_id: uuid.UUID
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    academic_year: str
    semester: int
    attendance_date: datetime
    session_name: str
    attendance_status: AttendanceStatus
    source_type: str
    verification_status: RecordVerificationStatus
    recorded_by: Optional[uuid.UUID] = None
    verified_by: Optional[uuid.UUID] = None
    source_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Import Management Schemas ---

class AcademicImportErrorResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    row_number: int
    column_name: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_code: str
    error_message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicImportJobResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    uploaded_by: Optional[uuid.UUID] = None
    file_name: str
    file_size_bytes: int
    mime_type: str
    storage_path: str
    import_category: ImportCategory
    status: ImportJobStatus
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    imported_rows: int
    preview_data: Optional[List[Dict[str, Any]]] = None
    error_summary: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicImportConfirmRequest(BaseModel):
    allow_partial: bool = Field(default=True, description="Import all valid rows even if invalid rows exist")


# --- Data Quality Intelligence Schemas ---

class AcademicDataQualityFindingResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    rule_identifier: str
    entity_type: str
    entity_id: uuid.UUID
    severity: DataQualitySeverity
    description: str
    source_record: Optional[Dict[str, Any]] = None
    recommended_action: Optional[str] = None
    resolution_status: str
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Verification & Audit Schemas ---

class RecordVerificationRequest(BaseModel):
    action: str = Field(..., json_schema_extra={"example": "VERIFY"})  # VERIFY, REJECT, REQUEST_CORRECTION
    reason: Optional[str] = Field(None, json_schema_extra={"example": "Verified against physical exam answer sheets."})


class RecordCorrectionRequest(BaseModel):
    marks_obtained: Optional[float] = Field(None, ge=0)
    result_status: Optional[AssessmentResultStatus] = None
    attendance_status: Optional[AttendanceStatus] = None
    reason: str = Field(..., json_schema_extra={"example": "Faculty re-evaluation correction."})


class AcademicRecordAuditResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    actor_name: Optional[str] = None
    action: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- High-Level Overview Aggregation ---

class AcademicDataOverviewResponse(BaseModel):
    total_students: int
    active_enrollments: int
    total_assessments: int
    performance_records_count: int
    attendance_records_count: int
    pending_verifications_count: int
    data_quality_issues_count: int
    total_import_jobs: int
