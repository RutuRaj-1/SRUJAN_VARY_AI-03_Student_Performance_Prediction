import os
import csv
import io
import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import openpyxl
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.academic_data import (
    AcademicImportJob,
    AcademicImportError,
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.syllabus import AcademicProgram, AcademicSubject
from app.models.enums import (
    ImportCategory,
    ImportJobStatus,
    AssessmentType,
    AssessmentResultStatus,
    AttendanceStatus,
    RecordVerificationStatus,
)
from app.core.logging import logger

UPLOAD_IMPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads/academic_imports"))
ALLOWED_IMPORT_EXTENSIONS = {".csv", ".xlsx"}
MAX_IMPORT_FILE_SIZE = 15 * 1024 * 1024  # 15 MB


class AcademicImportService:
    def __init__(self):
        os.makedirs(UPLOAD_IMPORT_DIR, exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile, institution_id: uuid.UUID) -> Tuple[str, int, str]:
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if ext not in ALLOWED_IMPORT_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Only CSV (.csv) and Excel (.xlsx) files are allowed.",
            )

        inst_dir = os.path.join(UPLOAD_IMPORT_DIR, str(institution_id))
        os.makedirs(inst_dir, exist_ok=True)

        target_path = os.path.join(inst_dir, f"{uuid.uuid4()}{ext}")
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_IMPORT_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 15MB limit.",
            )

        with open(target_path, "wb") as f:
            f.write(content)

        await file.seek(0)
        return target_path, file_size, ext

    def parse_raw_rows(self, file_path: str, ext: str) -> List[Dict[str, Any]]:
        rows = []
        if ext == ".csv":
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    # Strip whitespace from keys and values
                    clean_row = {k.strip().lower(): v.strip() if isinstance(v, str) else v for k, v in r.items() if k}
                    if any(clean_row.values()):
                        rows.append(clean_row)
        elif ext == ".xlsx":
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            headers = []
            for col_idx, cell in enumerate(sheet.iter_rows(min_row=1, max_row=1, values_only=True)):
                headers = [str(c).strip().lower() for c in cell if c is not None]
                break

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                row_dict = {}
                for idx, val in enumerate(row):
                    if idx < len(headers):
                        row_dict[headers[idx]] = str(val).strip() if val is not None else ""
                rows.append(row_dict)
            wb.close()
        return rows

    def create_import_job(
        self,
        db: Session,
        institution_id: uuid.UUID,
        uploader_id: uuid.UUID,
        file_name: str,
        file_size: int,
        storage_path: str,
        category: ImportCategory,
        ext: str,
    ) -> AcademicImportJob:
        raw_rows = self.parse_raw_rows(storage_path, ext)
        total_rows = len(raw_rows)

        # Validate rows according to category
        valid_rows, invalid_rows, duplicate_rows, errors = self._validate_category_rows(
            db, institution_id, category, raw_rows
        )

        job = AcademicImportJob(
            id=uuid.uuid4(),
            institution_id=institution_id,
            uploaded_by=uploader_id,
            file_name=file_name,
            file_size_bytes=file_size,
            mime_type="text/csv" if ext == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            storage_path=storage_path,
            import_category=category.value,
            status=ImportJobStatus.PREVIEW_READY.value,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            duplicate_rows=duplicate_rows,
            imported_rows=0,
            preview_data=raw_rows[:25],
            error_summary={"total_errors": len(errors), "sample_errors": [e.error_message for e in errors[:5]]},
        )
        db.add(job)
        db.flush()

        for err in errors:
            err.job_id = job.id
            db.add(err)

        db.commit()
        db.refresh(job)
        return job

    def _validate_category_rows(
        self,
        db: Session,
        institution_id: uuid.UUID,
        category: ImportCategory,
        rows: List[Dict[str, Any]],
    ) -> Tuple[int, int, int, List[AcademicImportError]]:
        valid_count = 0
        invalid_count = 0
        duplicate_count = 0
        errors: List[AcademicImportError] = []

        seen_keys = set()

        for idx, row in enumerate(rows, start=2):
            row_errors = []

            if category == ImportCategory.STUDENTS:
                enr = row.get("enrollment_number", "").strip()
                fname = row.get("first_name", "").strip()
                lname = row.get("last_name", "").strip()
                prog_code = row.get("program_code", "").strip()

                if not enr:
                    row_errors.append(("enrollment_number", "MISSING_ENROLLMENT", "Enrollment number is required."))
                elif enr in seen_keys:
                    duplicate_count += 1
                    row_errors.append(("enrollment_number", "DUPLICATE_IN_FILE", f"Duplicate enrollment number '{enr}' in spreadsheet."))
                else:
                    seen_keys.add(enr)
                    # Check DB existence
                    stmt = select(StudentAcademicProfile).where(
                        and_(
                            StudentAcademicProfile.institution_id == institution_id,
                            StudentAcademicProfile.enrollment_number == enr,
                        )
                    )
                    if db.execute(stmt).scalars().first():
                        duplicate_count += 1
                        row_errors.append(("enrollment_number", "DUPLICATE_IN_DB", f"Student '{enr}' already exists in database."))

                if not fname:
                    row_errors.append(("first_name", "MISSING_NAME", "First name is required."))
                if not lname:
                    row_errors.append(("last_name", "MISSING_NAME", "Last name is required."))

                if prog_code:
                    prog_stmt = select(AcademicProgram).where(
                        and_(AcademicProgram.institution_id == institution_id, AcademicProgram.code == prog_code)
                    )
                    if not db.execute(prog_stmt).scalars().first():
                        row_errors.append(("program_code", "INVALID_PROGRAM", f"Program code '{prog_code}' not found."))

            elif category == ImportCategory.PERFORMANCE:
                enr = row.get("enrollment_number", "").strip()
                subj_code = row.get("subject_code", "").strip()
                asmt_name = row.get("assessment_name", "").strip()
                marks_str = row.get("marks_obtained", "").strip()

                if not enr or not subj_code or not asmt_name:
                    row_errors.append(("general", "MISSING_FIELDS", "enrollment_number, subject_code, and assessment_name are required."))

                # Check student
                stud_stmt = select(StudentAcademicProfile).where(
                    and_(StudentAcademicProfile.institution_id == institution_id, StudentAcademicProfile.enrollment_number == enr)
                )
                student = db.execute(stud_stmt).scalars().first()
                if not student:
                    row_errors.append(("enrollment_number", "STUDENT_NOT_FOUND", f"Student '{enr}' not found in institution."))

                # Check assessment
                subj_stmt = select(AcademicSubject).where(
                    and_(AcademicSubject.institution_id == institution_id, AcademicSubject.code == subj_code)
                )
                subject = db.execute(subj_stmt).scalars().first()
                if not subject:
                    row_errors.append(("subject_code", "SUBJECT_NOT_FOUND", f"Subject '{subj_code}' not found in institution."))
                else:
                    asmt_stmt = select(AcademicAssessment).where(
                        and_(AcademicAssessment.subject_id == subject.id, AcademicAssessment.assessment_name == asmt_name)
                    )
                    assessment = db.execute(asmt_stmt).scalars().first()
                    if not assessment:
                        row_errors.append(("assessment_name", "ASSESSMENT_NOT_FOUND", f"Assessment '{asmt_name}' not found for subject '{subj_code}'."))
                    elif marks_str:
                        try:
                            marks = float(marks_str)
                            if marks < 0:
                                row_errors.append(("marks_obtained", "NEGATIVE_MARKS", f"Marks cannot be negative ({marks})."))
                            elif marks > assessment.maximum_marks:
                                row_errors.append(("marks_obtained", "EXCEEDS_MAX", f"Marks ({marks}) exceed maximum marks ({assessment.maximum_marks})."))
                        except ValueError:
                            row_errors.append(("marks_obtained", "INVALID_NUMBER", f"'{marks_str}' is not a valid number."))

            elif category == ImportCategory.ATTENDANCE:
                enr = row.get("enrollment_number", "").strip()
                subj_code = row.get("subject_code", "").strip()
                date_str = row.get("attendance_date", "").strip()

                if not enr or not subj_code or not date_str:
                    row_errors.append(("general", "MISSING_FIELDS", "enrollment_number, subject_code, and attendance_date are required."))

            if row_errors:
                invalid_count += 1
                for col, code, msg in row_errors:
                    errors.append(
                        AcademicImportError(
                            id=uuid.uuid4(),
                            job_id=uuid.uuid4(),  # updated after job creation
                            row_number=idx,
                            column_name=col,
                            raw_data=row,
                            error_code=code,
                            error_message=msg,
                        )
                    )
            else:
                valid_count += 1

        return valid_count, invalid_count, duplicate_count, errors

    def execute_import_job(
        self,
        db: Session,
        job_id: uuid.UUID,
        institution_id: uuid.UUID,
        executor_id: uuid.UUID,
        allow_partial: bool = True,
    ) -> AcademicImportJob:
        job = db.get(AcademicImportJob, job_id)
        if not job or job.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found.")

        if job.status == ImportJobStatus.COMPLETED.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has already been imported.")

        if not allow_partial and job.invalid_rows > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Import rejected: file contains {job.invalid_rows} invalid rows and allow_partial is False.",
            )

        job.status = ImportJobStatus.IMPORTING.value
        db.commit()

        try:
            ext = os.path.splitext(job.storage_path)[1].lower()
            raw_rows = self.parse_raw_rows(job.storage_path, ext)
            imported_count = 0

            # Import according to category
            if job.import_category == ImportCategory.STUDENTS.value:
                imported_count = self._execute_students_import(db, institution_id, raw_rows)
            elif job.import_category == ImportCategory.PERFORMANCE.value:
                imported_count = self._execute_performance_import(db, institution_id, executor_id, raw_rows, str(job.id))
            elif job.import_category == ImportCategory.ATTENDANCE.value:
                imported_count = self._execute_attendance_import(db, institution_id, executor_id, raw_rows, str(job.id))

            job.status = ImportJobStatus.COMPLETED.value
            job.imported_rows = imported_count
            job.completed_at = datetime.now()
            db.commit()
            db.refresh(job)
            return job
        except Exception as exc:
            db.rollback()
            job.status = ImportJobStatus.FAILED.value
            job.error_summary = {"execution_error": str(exc)}
            db.commit()
            logger.error("Import job %s execution failed: %s", job.id, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import execution failed: {str(exc)}",
            )

    def _execute_students_import(self, db: Session, institution_id: uuid.UUID, rows: List[Dict[str, Any]]) -> int:
        count = 0
        seen_in_batch = set()
        for row in rows:
            enr = row.get("enrollment_number", "").strip()
            fname = row.get("first_name", "").strip()
            lname = row.get("last_name", "").strip()
            prog_code = row.get("program_code", "").strip()

            if not enr or not fname or not lname or enr in seen_in_batch:
                continue
            seen_in_batch.add(enr)

            # Skip existing
            existing = db.execute(
                select(StudentAcademicProfile).where(
                    and_(
                        StudentAcademicProfile.institution_id == institution_id,
                        StudentAcademicProfile.enrollment_number == enr,
                    )
                )
            ).scalars().first()
            if existing:
                continue

            # Program lookup or default
            prog = None
            if prog_code:
                prog = db.execute(
                    select(AcademicProgram).where(
                        and_(AcademicProgram.institution_id == institution_id, AcademicProgram.code == prog_code)
                    )
                ).scalars().first()

            if not prog:
                prog = db.execute(
                    select(AcademicProgram).where(AcademicProgram.institution_id == institution_id)
                ).scalars().first()

            if not prog:
                continue

            student = StudentAcademicProfile(
                id=uuid.uuid4(),
                institution_id=institution_id,
                program_id=prog.id,
                enrollment_number=enr,
                admission_number=row.get("admission_number", "").strip() or None,
                first_name=fname,
                last_name=lname,
                email=row.get("email", "").strip() or None,
                department=row.get("department", "").strip() or "General Engineering",
                admission_year=int(row.get("admission_year", 2024)),
                current_semester=int(row.get("current_semester", 1)),
                academic_status=row.get("academic_status", "ENROLLED").strip().upper(),
            )
            db.add(student)
            count += 1

        db.flush()
        return count

    def _execute_performance_import(
        self,
        db: Session,
        institution_id: uuid.UUID,
        executor_id: uuid.UUID,
        rows: List[Dict[str, Any]],
        source_ref: str,
    ) -> int:
        count = 0
        seen_perf = set()
        for row in rows:
            enr = row.get("enrollment_number", "").strip()
            subj_code = row.get("subject_code", "").strip()
            asmt_name = row.get("assessment_name", "").strip()
            marks_str = row.get("marks_obtained", "").strip()

            key = (enr, subj_code, asmt_name)
            if key in seen_perf:
                continue
            seen_perf.add(key)

            student = db.execute(
                select(StudentAcademicProfile).where(
                    and_(StudentAcademicProfile.institution_id == institution_id, StudentAcademicProfile.enrollment_number == enr)
                )
            ).scalars().first()

            subject = db.execute(
                select(AcademicSubject).where(
                    and_(AcademicSubject.institution_id == institution_id, AcademicSubject.code == subj_code)
                )
            ).scalars().first()

            if not student or not subject:
                continue

            assessment = db.execute(
                select(AcademicAssessment).where(
                    and_(AcademicAssessment.subject_id == subject.id, AcademicAssessment.assessment_name == asmt_name)
                )
            ).scalars().first()

            if not assessment:
                continue

            marks = None
            if marks_str:
                try:
                    marks = float(marks_str)
                    if marks < 0 or marks > assessment.maximum_marks:
                        continue
                except ValueError:
                    continue

            # Non-numeric result status
            status_val = row.get("result_status", "PASSED").strip().upper()
            if not marks and status_val == "PASSED":
                status_val = "NOT_SUBMITTED"

            record = StudentAssessmentRecord(
                id=uuid.uuid4(),
                institution_id=institution_id,
                student_id=student.id,
                assessment_id=assessment.id,
                marks_obtained=marks,
                maximum_marks_snapshot=assessment.maximum_marks,
                result_status=status_val,
                source_type="IMPORT",
                verification_status=RecordVerificationStatus.IMPORTED.value,
                recorded_by=executor_id,
                source_reference=f"Import Job {source_ref[:8]}",
            )
            db.add(record)
            count += 1

        db.flush()
        return count

    def _execute_attendance_import(
        self,
        db: Session,
        institution_id: uuid.UUID,
        executor_id: uuid.UUID,
        rows: List[Dict[str, Any]],
        source_ref: str,
    ) -> int:
        count = 0
        seen_att = set()
        for row in rows:
            enr = row.get("enrollment_number", "").strip()
            subj_code = row.get("subject_code", "").strip()
            date_str = row.get("attendance_date", "").strip()
            status_str = row.get("attendance_status", "PRESENT").strip().upper()
            session_name = row.get("session_name", "Regular Session").strip()

            key = (enr, subj_code, date_str, session_name)
            if key in seen_att:
                continue
            seen_att.add(key)

            student = db.execute(
                select(StudentAcademicProfile).where(
                    and_(StudentAcademicProfile.institution_id == institution_id, StudentAcademicProfile.enrollment_number == enr)
                )
            ).scalars().first()

            subject = db.execute(
                select(AcademicSubject).where(
                    and_(AcademicSubject.institution_id == institution_id, AcademicSubject.code == subj_code)
                )
            ).scalars().first()

            if not student or not subject:
                continue

            try:
                att_date = datetime.fromisoformat(date_str)
            except ValueError:
                att_date = datetime.now()

            record = StudentAttendanceRecord(
                id=uuid.uuid4(),
                institution_id=institution_id,
                student_id=student.id,
                subject_id=subject.id,
                academic_year=row.get("academic_year", "2024-2025").strip(),
                semester=int(row.get("semester", subject.semester)),
                attendance_date=att_date,
                session_name=row.get("session_name", "Regular Session").strip(),
                attendance_status=status_str if status_str in AttendanceStatus._member_names_ else AttendanceStatus.PRESENT.value,
                source_type="IMPORT",
                verification_status=RecordVerificationStatus.IMPORTED.value,
                recorded_by=executor_id,
                source_reference=f"Import Job {source_ref[:8]}",
            )
            db.add(record)
            count += 1

        db.flush()
        return count


import_service = AcademicImportService()
