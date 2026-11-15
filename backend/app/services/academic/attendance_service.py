import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models.academic_data import (
    StudentAttendanceRecord,
    StudentAcademicProfile,
)
from app.models.syllabus import AcademicSubject
from app.models.enums import AttendanceStatus, RecordVerificationStatus
from app.schemas.academic_data import StudentAttendanceRecordCreate


class AttendanceService:
    def record_attendance(
        self,
        db: Session,
        recorder_id: uuid.UUID,
        data: StudentAttendanceRecordCreate,
    ) -> StudentAttendanceRecord:
        # Validate student
        student = db.get(StudentAcademicProfile, data.student_id)
        if not student or student.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not belong to institution.")

        # Validate subject
        subject = db.get(AcademicSubject, data.subject_id)
        if not subject or subject.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject does not belong to institution.")

        # Check existing record for same session
        stmt = select(StudentAttendanceRecord).where(
            and_(
                StudentAttendanceRecord.student_id == data.student_id,
                StudentAttendanceRecord.subject_id == data.subject_id,
                StudentAttendanceRecord.attendance_date == data.attendance_date,
                StudentAttendanceRecord.session_name == data.session_name,
            )
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            if existing.verification_status == RecordVerificationStatus.VERIFIED.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot overwrite verified attendance record without audited correction.",
                )
            existing.attendance_status = data.attendance_status.value
            existing.source_type = data.source_type
            existing.source_reference = data.source_reference
            existing.recorded_by = recorder_id
            db.commit()
            db.refresh(existing)
            return existing

        record = StudentAttendanceRecord(
            id=uuid.uuid4(),
            institution_id=data.institution_id,
            student_id=data.student_id,
            subject_id=data.subject_id,
            academic_year=data.academic_year,
            semester=data.semester,
            attendance_date=data.attendance_date,
            session_name=data.session_name,
            attendance_status=data.attendance_status.value,
            source_type=data.source_type,
            verification_status=data.verification_status.value,
            recorded_by=recorder_id,
            source_reference=data.source_reference,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_student_attendance(
        self,
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
        semester: Optional[int] = None,
    ) -> List[StudentAttendanceRecord]:
        stmt = select(StudentAttendanceRecord).where(
            and_(
                StudentAttendanceRecord.student_id == student_id,
                StudentAttendanceRecord.institution_id == institution_id,
            )
        )
        if subject_id:
            stmt = stmt.where(StudentAttendanceRecord.subject_id == subject_id)
        if semester:
            stmt = stmt.where(StudentAttendanceRecord.semester == semester)
        return db.execute(stmt.order_by(StudentAttendanceRecord.attendance_date.desc())).scalars().all()


attendance_service = AttendanceService()
