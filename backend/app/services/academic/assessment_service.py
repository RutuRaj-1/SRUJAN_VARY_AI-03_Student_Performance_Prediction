import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models.academic_data import (
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAcademicProfile,
)
from app.models.syllabus import AcademicSubject
from app.models.enums import AssessmentResultStatus, RecordVerificationStatus
from app.schemas.academic_data import (
    AcademicAssessmentCreate,
    StudentAssessmentRecordCreate,
)


class AssessmentService:
    def create_assessment(
        self,
        db: Session,
        creator_id: uuid.UUID,
        data: AcademicAssessmentCreate,
    ) -> AcademicAssessment:
        # Validate subject
        subject = db.get(AcademicSubject, data.subject_id)
        if not subject or subject.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject does not belong to institution.")

        # Check uniqueness within term
        stmt = select(AcademicAssessment).where(
            and_(
                AcademicAssessment.subject_id == data.subject_id,
                AcademicAssessment.academic_year == data.academic_year,
                AcademicAssessment.semester == data.semester,
                AcademicAssessment.assessment_name == data.assessment_name,
            )
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Assessment '{data.assessment_name}' already exists for this subject, term, and year.",
            )

        assessment = AcademicAssessment(
            id=uuid.uuid4(),
            institution_id=data.institution_id,
            subject_id=data.subject_id,
            academic_year=data.academic_year,
            semester=data.semester,
            assessment_name=data.assessment_name,
            assessment_type=data.assessment_type.value,
            maximum_marks=data.maximum_marks,
            passing_marks=data.passing_marks,
            weightage_percentage=data.weightage_percentage,
            assessment_date=data.assessment_date,
            description=data.description,
            created_by=creator_id,
            status=data.status,
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    def list_assessments(
        self,
        db: Session,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[AcademicAssessment]:
        stmt = select(AcademicAssessment).where(AcademicAssessment.institution_id == institution_id)
        if subject_id:
            stmt = stmt.where(AcademicAssessment.subject_id == subject_id)
        if academic_year:
            stmt = stmt.where(AcademicAssessment.academic_year == academic_year)
        if semester:
            stmt = stmt.where(AcademicAssessment.semester == semester)
        return db.execute(stmt.order_by(AcademicAssessment.created_at.desc())).scalars().all()

    def record_student_performance(
        self,
        db: Session,
        recorder_id: uuid.UUID,
        data: StudentAssessmentRecordCreate,
    ) -> StudentAssessmentRecord:
        # Validate assessment exists
        assessment = db.get(AcademicAssessment, data.assessment_id)
        if not assessment or assessment.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid assessment specified.")

        # Validate student exists
        student = db.get(StudentAcademicProfile, data.student_id)
        if not student or student.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not belong to institution.")

        # Marks boundary validation
        if data.marks_obtained is not None:
            if data.marks_obtained < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marks obtained cannot be negative (Received {data.marks_obtained}).",
                )
            if data.marks_obtained > assessment.maximum_marks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marks obtained ({data.marks_obtained}) cannot exceed maximum marks ({assessment.maximum_marks}).",
                )

        # Check existing record
        stmt = select(StudentAssessmentRecord).where(
            and_(
                StudentAssessmentRecord.student_id == data.student_id,
                StudentAssessmentRecord.assessment_id == data.assessment_id,
            )
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            if existing.verification_status == RecordVerificationStatus.VERIFIED.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot overwrite a verified assessment record. Please use the audited correction workflow.",
                )
            # Update unverified record
            existing.marks_obtained = data.marks_obtained
            existing.result_status = data.result_status.value
            existing.remarks = data.remarks
            existing.source_type = data.source_type
            existing.source_reference = data.source_reference
            existing.recorded_by = recorder_id
            db.commit()
            db.refresh(existing)
            return existing

        record = StudentAssessmentRecord(
            id=uuid.uuid4(),
            institution_id=data.institution_id,
            student_id=data.student_id,
            assessment_id=data.assessment_id,
            marks_obtained=data.marks_obtained,
            maximum_marks_snapshot=assessment.maximum_marks,
            result_status=data.result_status.value,
            source_type=data.source_type,
            verification_status=data.verification_status.value,
            recorded_by=recorder_id,
            source_reference=data.source_reference,
            remarks=data.remarks,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_student_performance(
        self,
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> List[StudentAssessmentRecord]:
        stmt = (
            select(StudentAssessmentRecord)
            .where(
                and_(
                    StudentAssessmentRecord.student_id == student_id,
                    StudentAssessmentRecord.institution_id == institution_id,
                )
            )
            .order_by(StudentAssessmentRecord.created_at.desc())
        )
        return db.execute(stmt).scalars().all()


assessment_service = AssessmentService()
