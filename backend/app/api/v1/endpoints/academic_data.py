import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_active_user, CurrentUser, require_roles
from app.models.enums import UserRole, ImportCategory
from app.schemas.academic_data import (
    StudentAcademicProfileCreate,
    StudentAcademicProfileUpdate,
    StudentAcademicProfileResponse,
    StudentSubjectEnrollmentCreate,
    StudentSubjectEnrollmentResponse,
    AcademicAssessmentCreate,
    AcademicAssessmentResponse,
    StudentAssessmentRecordCreate,
    StudentAssessmentRecordResponse,
    StudentAttendanceRecordCreate,
    StudentAttendanceRecordResponse,
    AcademicImportJobResponse,
    AcademicImportErrorResponse,
    AcademicImportConfirmRequest,
    AcademicDataQualityFindingResponse,
    AcademicRecordAuditResponse,
    RecordVerificationRequest,
    RecordCorrectionRequest,
    AcademicDataOverviewResponse,
)
from app.services.academic.student_service import student_academic_service
from app.services.academic.assessment_service import assessment_service
from app.services.academic.attendance_service import attendance_service
from app.services.academic.import_service import import_service
from app.services.academic.quality_service import quality_service
from app.services.academic.verification_service import verification_service
from app.models.academic_data import AcademicImportJob, AcademicImportError, StudentAssessmentRecord

router = APIRouter()


def _resolve_institution_id(current_user: CurrentUser, requested_inst_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    if current_user.role == UserRole.SUPER_ADMIN:
        if requested_inst_id:
            return requested_inst_id
        if current_user.institution_id:
            return uuid.UUID(current_user.institution_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="institution_id parameter required for platform admin.")
    if not current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not assigned to an institution.")
    return uuid.UUID(current_user.institution_id)


# --- Overview & Summary ---

@router.get("/overview", response_model=AcademicDataOverviewResponse)
def get_academic_overview(
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return verification_service.get_overview_metrics(db, inst_id)


# --- Student Academic Profiles ---

@router.post("/students", response_model=StudentAcademicProfileResponse, status_code=status.HTTP_201_CREATED)
def create_student_academic_profile(
    student_in: StudentAcademicProfileCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(student_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create student profile for another institution.")
    return student_academic_service.create_student_profile(db, student_in)


@router.get("/students", response_model=List[StudentAcademicProfileResponse])
def list_student_academic_profiles(
    program_id: Optional[uuid.UUID] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    institution_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return student_academic_service.list_student_profiles(
        db, inst_id, program_id=program_id, semester=semester, search=search, skip=skip, limit=limit
    )


@router.get("/students/{student_id}", response_model=StudentAcademicProfileResponse)
def get_student_academic_profile(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id) if current_user.role != UserRole.SUPER_ADMIN and current_user.institution_id else None
    return student_academic_service.get_student_profile(db, student_id, inst_id)


@router.patch("/students/{student_id}", response_model=StudentAcademicProfileResponse)
def update_student_academic_profile(
    student_id: uuid.UUID,
    student_update: StudentAcademicProfileUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user)
    return student_academic_service.update_student_profile(db, student_id, inst_id, student_update)


# --- Enrollments ---

@router.post("/enrollments", response_model=StudentSubjectEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student_in_subject(
    enrollment_in: StudentSubjectEnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(enrollment_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot enroll student for another institution.")
    return student_academic_service.enroll_student_in_subject(db, enrollment_in)


@router.get("/students/{student_id}/enrollments", response_model=List[StudentSubjectEnrollmentResponse])
def list_student_enrollments(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user)
    return student_academic_service.list_student_enrollments(db, student_id, inst_id)


# --- Academic Assessments ---

@router.post("/assessments", response_model=AcademicAssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_academic_assessment(
    assessment_in: AcademicAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(assessment_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create assessment for another institution.")
    creator_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return assessment_service.create_assessment(db, creator_id, assessment_in)


@router.get("/assessments", response_model=List[AcademicAssessmentResponse])
def list_academic_assessments(
    subject_id: Optional[uuid.UUID] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return assessment_service.list_assessments(db, inst_id, subject_id, academic_year, semester)


# --- Student Performance Records ---

@router.post("/performance", response_model=StudentAssessmentRecordResponse, status_code=status.HTTP_201_CREATED)
def record_student_performance(
    record_in: StudentAssessmentRecordCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(record_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot record performance for another institution.")
    recorder_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return assessment_service.record_student_performance(db, recorder_id, record_in)


@router.get("/performance", response_model=List[StudentAssessmentRecordResponse])
def query_performance_records(
    assessment_id: Optional[uuid.UUID] = None,
    student_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user)
    query = select(StudentAssessmentRecord).where(StudentAssessmentRecord.institution_id == inst_id)
    if assessment_id:
        query = query.where(StudentAssessmentRecord.assessment_id == assessment_id)
    if student_id:
        query = query.where(StudentAssessmentRecord.student_id == student_id)
    return list(db.execute(query).scalars().all())


@router.get("/students/{student_id}/performance", response_model=List[StudentAssessmentRecordResponse])
def list_student_performance(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user)
    return assessment_service.list_student_performance(db, student_id, inst_id)


# --- Attendance Records ---

@router.post("/attendance", response_model=StudentAttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
def record_student_attendance(
    attendance_in: StudentAttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    if current_user.role != UserRole.SUPER_ADMIN and str(attendance_in.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot record attendance for another institution.")
    recorder_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return attendance_service.record_attendance(db, recorder_id, attendance_in)


@router.get("/students/{student_id}/attendance", response_model=List[StudentAttendanceRecordResponse])
def list_student_attendance(
    student_id: uuid.UUID,
    subject_id: Optional[uuid.UUID] = None,
    semester: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user)
    return attendance_service.list_student_attendance(db, student_id, inst_id, subject_id, semester)


# --- Import Management Workflows ---

@router.post("/imports", response_model=AcademicImportJobResponse, status_code=status.HTTP_201_CREATED)
async def upload_academic_import(
    file: UploadFile = File(...),
    category: ImportCategory = Form(...),
    institution_id: Optional[uuid.UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    storage_path, file_size, ext = await import_service.save_uploaded_file(file, inst_id)
    uploader_id = uuid.UUID(current_user.user_id) if current_user.user_id else None

    return import_service.create_import_job(
        db=db,
        institution_id=inst_id,
        uploader_id=uploader_id,
        file_name=file.filename or "import_data",
        file_size=file_size,
        storage_path=storage_path,
        category=category,
        ext=ext,
    )


@router.get("/imports", response_model=List[AcademicImportJobResponse])
def list_academic_imports(
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    stmt = (
        select(AcademicImportJob)
        .where(AcademicImportJob.institution_id == inst_id)
        .order_by(AcademicImportJob.created_at.desc())
    )
    return db.execute(stmt).scalars().all()


@router.get("/imports/{job_id}", response_model=AcademicImportJobResponse)
def get_academic_import_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    job = db.get(AcademicImportJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found.")
    if current_user.role != UserRole.SUPER_ADMIN and str(job.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return job


@router.post("/imports/{job_id}/confirm", response_model=AcademicImportJobResponse)
def confirm_academic_import(
    job_id: uuid.UUID,
    confirm_in: AcademicImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user)
    executor_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return import_service.execute_import_job(db, job_id, inst_id, executor_id, confirm_in.allow_partial)


@router.get("/imports/{job_id}/errors", response_model=List[AcademicImportErrorResponse])
def get_import_errors(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    job = db.get(AcademicImportJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found.")
    if current_user.role != UserRole.SUPER_ADMIN and str(job.institution_id) != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    stmt = select(AcademicImportError).where(AcademicImportError.job_id == job_id).order_by(AcademicImportError.row_number.asc())
    return db.execute(stmt).scalars().all()


# --- Data Quality Intelligence ---

@router.post("/quality/scan", response_model=List[AcademicDataQualityFindingResponse])
def scan_data_quality(
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return quality_service.scan_institution_data_quality(db, inst_id)


@router.get("/quality", response_model=List[AcademicDataQualityFindingResponse])
def list_data_quality_findings(
    severity: Optional[str] = None,
    entity_type: Optional[str] = None,
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return quality_service.list_findings(db, inst_id, severity, entity_type)


@router.post("/quality/{finding_id}/resolve", response_model=AcademicDataQualityFindingResponse)
def resolve_data_quality_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    resolver_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    resolved = quality_service.resolve_finding(db, finding_id, resolver_id)
    if not resolved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data quality finding not found.")
    return resolved


# --- Record Verification & Audited Corrections ---

@router.post("/records/{record_id}/verify", response_model=StudentAssessmentRecordResponse)
def verify_academic_record(
    record_id: uuid.UUID,
    verify_in: RecordVerificationRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user)
    verifier_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return verification_service.verify_performance_record(db, record_id, verifier_id, inst_id, verify_in)


@router.post("/records/{record_id}/correction", response_model=StudentAssessmentRecordResponse)
def correct_academic_record(
    record_id: uuid.UUID,
    correction_in: RecordCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY)),
):
    inst_id = _resolve_institution_id(current_user)
    corrector_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return verification_service.correct_performance_record(db, record_id, corrector_id, inst_id, correction_in)


@router.get("/audits", response_model=List[AcademicRecordAuditResponse])
def get_academic_audits(
    entity_id: Optional[uuid.UUID] = None,
    entity_type: Optional[str] = None,
    institution_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _resolve_institution_id(current_user, institution_id)
    return verification_service.get_audit_trail(db, inst_id, entity_id, entity_type)
