import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models.academic_data import StudentAcademicProfile, StudentSubjectEnrollment
from app.models.syllabus import AcademicProgram, AcademicSubject
from app.schemas.academic_data import (
    StudentAcademicProfileCreate,
    StudentAcademicProfileUpdate,
    StudentSubjectEnrollmentCreate,
)


class StudentAcademicService:
    def create_student_profile(
        self,
        db: Session,
        data: StudentAcademicProfileCreate,
    ) -> StudentAcademicProfile:
        # Check uniqueness within institution
        stmt = select(StudentAcademicProfile).where(
            and_(
                StudentAcademicProfile.institution_id == data.institution_id,
                StudentAcademicProfile.enrollment_number == data.enrollment_number,
            )
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with enrollment number '{data.enrollment_number}' already exists in this institution.",
            )

        # Validate program exists
        program = db.get(AcademicProgram, data.program_id)
        if not program or program.institution_id != data.institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid program_id specified for this institution.",
            )

        student = StudentAcademicProfile(
            id=uuid.uuid4(),
            institution_id=data.institution_id,
            profile_id=data.profile_id,
            program_id=data.program_id,
            enrollment_number=data.enrollment_number,
            admission_number=data.admission_number,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            department=data.department,
            admission_year=data.admission_year,
            current_semester=data.current_semester,
            academic_status=data.academic_status,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    def get_student_profile(
        self,
        db: Session,
        student_id: uuid.UUID,
        institution_id: Optional[uuid.UUID] = None,
    ) -> StudentAcademicProfile:
        student = db.get(StudentAcademicProfile, student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
        if institution_id and student.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to student profile denied.")
        return student

    def list_student_profiles(
        self,
        db: Session,
        institution_id: uuid.UUID,
        program_id: Optional[uuid.UUID] = None,
        semester: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StudentAcademicProfile]:
        stmt = select(StudentAcademicProfile).where(StudentAcademicProfile.institution_id == institution_id)
        if program_id:
            stmt = stmt.where(StudentAcademicProfile.program_id == program_id)
        if semester:
            stmt = stmt.where(StudentAcademicProfile.current_semester == semester)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                (StudentAcademicProfile.first_name.ilike(pattern))
                | (StudentAcademicProfile.last_name.ilike(pattern))
                | (StudentAcademicProfile.enrollment_number.ilike(pattern))
                | (StudentAcademicProfile.email.ilike(pattern))
            )
        stmt = stmt.order_by(StudentAcademicProfile.enrollment_number.asc()).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    def update_student_profile(
        self,
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
        data: StudentAcademicProfileUpdate,
    ) -> StudentAcademicProfile:
        student = self.get_student_profile(db, student_id, institution_id)
        
        if data.first_name is not None:
            student.first_name = data.first_name
        if data.last_name is not None:
            student.last_name = data.last_name
        if data.email is not None:
            student.email = data.email
        if data.department is not None:
            student.department = data.department
        if data.current_semester is not None:
            student.current_semester = data.current_semester
        if data.academic_status is not None:
            student.academic_status = data.academic_status
        if data.program_id is not None:
            prog = db.get(AcademicProgram, data.program_id)
            if not prog or prog.institution_id != institution_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid program specified.")
            student.program_id = data.program_id
        if data.profile_id is not None:
            student.profile_id = data.profile_id

        db.commit()
        db.refresh(student)
        return student

    def enroll_student_in_subject(
        self,
        db: Session,
        data: StudentSubjectEnrollmentCreate,
    ) -> StudentSubjectEnrollment:
        # Verify student
        student = db.get(StudentAcademicProfile, data.student_id)
        if not student or student.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not belong to institution.")

        # Verify subject
        subject = db.get(AcademicSubject, data.subject_id)
        if not subject or subject.institution_id != data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject does not belong to institution.")

        # Prevent duplicate enrollment
        stmt = select(StudentSubjectEnrollment).where(
            and_(
                StudentSubjectEnrollment.student_id == data.student_id,
                StudentSubjectEnrollment.subject_id == data.subject_id,
                StudentSubjectEnrollment.academic_year == data.academic_year,
                StudentSubjectEnrollment.semester == data.semester,
            )
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student is already enrolled in this subject for the specified academic year and semester.",
            )

        enrollment = StudentSubjectEnrollment(
            id=uuid.uuid4(),
            institution_id=data.institution_id,
            student_id=data.student_id,
            subject_id=data.subject_id,
            academic_year=data.academic_year,
            semester=data.semester,
            enrollment_status=data.enrollment_status,
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    def list_student_enrollments(
        self,
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> List[StudentSubjectEnrollment]:
        # Validate ownership
        self.get_student_profile(db, student_id, institution_id)
        stmt = (
            select(StudentSubjectEnrollment)
            .where(StudentSubjectEnrollment.student_id == student_id)
            .order_by(StudentSubjectEnrollment.semester.desc(), StudentSubjectEnrollment.academic_year.desc())
        )
        return db.execute(stmt).scalars().all()


student_academic_service = StudentAcademicService()
