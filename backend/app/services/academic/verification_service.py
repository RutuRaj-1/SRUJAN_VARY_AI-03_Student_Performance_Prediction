import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.academic_data import (
    StudentAssessmentRecord,
    StudentAttendanceRecord,
    AcademicRecordAudit,
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    AcademicImportJob,
    AcademicDataQualityFinding,
)
from app.models.profile import Profile
from app.models.enums import RecordVerificationStatus, AssessmentResultStatus, AttendanceStatus
from app.schemas.academic_data import (
    RecordVerificationRequest,
    RecordCorrectionRequest,
    AcademicRecordAuditResponse,
    AcademicDataOverviewResponse,
)


class AcademicVerificationService:
    def verify_performance_record(
        self,
        db: Session,
        record_id: uuid.UUID,
        verifier_id: uuid.UUID,
        institution_id: uuid.UUID,
        request: RecordVerificationRequest,
    ) -> StudentAssessmentRecord:
        record = db.get(StudentAssessmentRecord, record_id)
        if not record or record.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment record not found.")

        prev_status = record.verification_status
        action = request.action.upper()

        if action == "VERIFY":
            record.verification_status = RecordVerificationStatus.VERIFIED.value
        elif action == "REJECT":
            record.verification_status = RecordVerificationStatus.REJECTED.value
        elif action == "REQUEST_CORRECTION":
            record.verification_status = RecordVerificationStatus.CORRECTION_REQUIRED.value
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported verification action: {action}")

        record.verified_by = verifier_id
        record.verified_at = datetime.now()

        # Record audit log
        audit = AcademicRecordAudit(
            id=uuid.uuid4(),
            institution_id=institution_id,
            entity_type="PERFORMANCE",
            entity_id=record.id,
            actor_id=verifier_id,
            action=action,
            before_state={"verification_status": prev_status},
            after_state={"verification_status": record.verification_status},
            reason=request.reason,
        )
        db.add(audit)
        db.commit()
        db.refresh(record)
        return record

    def correct_performance_record(
        self,
        db: Session,
        record_id: uuid.UUID,
        corrector_id: uuid.UUID,
        institution_id: uuid.UUID,
        correction: RecordCorrectionRequest,
    ) -> StudentAssessmentRecord:
        record = db.get(StudentAssessmentRecord, record_id)
        if not record or record.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment record not found.")

        if not correction.reason or len(correction.reason.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A substantive audit reason (at least 5 characters) is required for correcting academic records.",
            )

        before_state = {
            "marks_obtained": record.marks_obtained,
            "result_status": record.result_status,
            "verification_status": record.verification_status,
        }

        # Validate marks boundary
        if correction.marks_obtained is not None:
            if correction.marks_obtained < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marks cannot be negative.")
            if correction.marks_obtained > record.maximum_marks_snapshot:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marks ({correction.marks_obtained}) exceed assessment maximum marks ({record.maximum_marks_snapshot}).",
                )
            record.marks_obtained = correction.marks_obtained

        if correction.result_status is not None:
            record.result_status = correction.result_status.value

        after_state = {
            "marks_obtained": record.marks_obtained,
            "result_status": record.result_status,
            "verification_status": record.verification_status,
        }

        # Log audit
        audit = AcademicRecordAudit(
            id=uuid.uuid4(),
            institution_id=institution_id,
            entity_type="PERFORMANCE",
            entity_id=record.id,
            actor_id=corrector_id,
            action="CORRECTED",
            before_state=before_state,
            after_state=after_state,
            reason=correction.reason,
        )
        db.add(audit)
        db.commit()
        db.refresh(record)
        return record

    def get_audit_trail(
        self,
        db: Session,
        institution_id: uuid.UUID,
        entity_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
    ) -> List[AcademicRecordAuditResponse]:
        stmt = (
            select(AcademicRecordAudit, Profile)
            .outerjoin(Profile, AcademicRecordAudit.actor_id == Profile.id)
            .where(AcademicRecordAudit.institution_id == institution_id)
        )
        if entity_id:
            stmt = stmt.where(AcademicRecordAudit.entity_id == entity_id)
        if entity_type:
            stmt = stmt.where(AcademicRecordAudit.entity_type == entity_type)

        results = db.execute(stmt.order_by(AcademicRecordAudit.created_at.desc())).all()
        audits = []
        for a, p in results:
            audits.append(
                AcademicRecordAuditResponse(
                    id=a.id,
                    institution_id=a.institution_id,
                    entity_type=a.entity_type,
                    entity_id=a.entity_id,
                    actor_id=a.actor_id,
                    actor_name=p.full_name if p else "System",
                    action=a.action,
                    before_state=a.before_state,
                    after_state=a.after_state,
                    reason=a.reason,
                    created_at=a.created_at,
                )
            )
        return audits

    def get_overview_metrics(
        self,
        db: Session,
        institution_id: uuid.UUID,
    ) -> AcademicDataOverviewResponse:
        total_students = db.scalar(
            select(func.count(StudentAcademicProfile.id)).where(StudentAcademicProfile.institution_id == institution_id)
        ) or 0

        active_enrollments = db.scalar(
            select(func.count(StudentSubjectEnrollment.id)).where(
                and_(
                    StudentSubjectEnrollment.institution_id == institution_id,
                    StudentSubjectEnrollment.enrollment_status == "ACTIVE",
                )
            )
        ) or 0

        total_assessments = db.scalar(
            select(func.count(AcademicAssessment.id)).where(AcademicAssessment.institution_id == institution_id)
        ) or 0

        perf_records = db.scalar(
            select(func.count(StudentAssessmentRecord.id)).where(StudentAssessmentRecord.institution_id == institution_id)
        ) or 0

        att_records = db.scalar(
            select(func.count(StudentAttendanceRecord.id)).where(StudentAttendanceRecord.institution_id == institution_id)
        ) or 0

        pending_verifications = db.scalar(
            select(func.count(StudentAssessmentRecord.id)).where(
                and_(
                    StudentAssessmentRecord.institution_id == institution_id,
                    StudentAssessmentRecord.verification_status.in_([
                        RecordVerificationStatus.IMPORTED.value,
                        RecordVerificationStatus.REVIEW_REQUIRED.value,
                    ]),
                )
            )
        ) or 0

        quality_issues = db.scalar(
            select(func.count(AcademicDataQualityFinding.id)).where(
                and_(
                    AcademicDataQualityFinding.institution_id == institution_id,
                    AcademicDataQualityFinding.resolution_status == "OPEN",
                )
            )
        ) or 0

        import_jobs = db.scalar(
            select(func.count(AcademicImportJob.id)).where(AcademicImportJob.institution_id == institution_id)
        ) or 0

        return AcademicDataOverviewResponse(
            total_students=total_students,
            active_enrollments=active_enrollments,
            total_assessments=total_assessments,
            performance_records_count=perf_records,
            attendance_records_count=att_records,
            pending_verifications_count=pending_verifications,
            data_quality_issues_count=quality_issues,
            total_import_jobs=import_jobs,
        )


verification_service = AcademicVerificationService()
