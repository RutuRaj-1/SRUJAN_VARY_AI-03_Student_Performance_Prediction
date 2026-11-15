import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.academic_data import (
    AcademicDataQualityFinding,
    StudentAcademicProfile,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.enums import DataQualitySeverity, AssessmentResultStatus


class AcademicDataQualityService:
    def scan_institution_data_quality(
        self,
        db: Session,
        institution_id: uuid.UUID,
    ) -> List[AcademicDataQualityFinding]:
        # Clear previous findings to prevent stale reports
        db.query(AcademicDataQualityFinding).filter(
            AcademicDataQualityFinding.institution_id == institution_id
        ).delete()

        findings: List[AcademicDataQualityFinding] = []

        # Rule 1: Check Student Profiles for Missing Contact / Program details
        students = db.execute(
            select(StudentAcademicProfile).where(StudentAcademicProfile.institution_id == institution_id)
        ).scalars().all()

        for s in students:
            if not s.email:
                findings.append(
                    AcademicDataQualityFinding(
                        id=uuid.uuid4(),
                        institution_id=institution_id,
                        rule_identifier="STUDENT_MISSING_EMAIL",
                        entity_type="STUDENT",
                        entity_id=s.id,
                        severity=DataQualitySeverity.WARNING.value,
                        description=f"Student '{s.enrollment_number}' ({s.first_name} {s.last_name}) has no recorded institutional email.",
                        source_record={"enrollment_number": s.enrollment_number, "first_name": s.first_name, "last_name": s.last_name},
                        recommended_action="Update student profile with verified institutional email address.",
                    )
                )

        # Rule 2: Check Assessments for Invalid Mark Boundaries or Passing Criteria
        assessments = db.execute(
            select(AcademicAssessment).where(AcademicAssessment.institution_id == institution_id)
        ).scalars().all()

        for a in assessments:
            if a.passing_marks and a.passing_marks > a.maximum_marks:
                findings.append(
                    AcademicDataQualityFinding(
                        id=uuid.uuid4(),
                        institution_id=institution_id,
                        rule_identifier="ASSESSMENT_PASSING_EXCEEDS_MAX",
                        entity_type="ASSESSMENT",
                        entity_id=a.id,
                        severity=DataQualitySeverity.CRITICAL.value,
                        description=f"Assessment '{a.assessment_name}' has passing marks ({a.passing_marks}) exceeding maximum marks ({a.maximum_marks}).",
                        source_record={"assessment_name": a.assessment_name, "max_marks": a.maximum_marks, "passing_marks": a.passing_marks},
                        recommended_action="Correct passing marks threshold to be less than maximum marks.",
                    )
                )

        # Rule 3: Check Performance Records for Negative or Out-of-Bound Marks
        perf_records = db.execute(
            select(StudentAssessmentRecord).where(StudentAssessmentRecord.institution_id == institution_id)
        ).scalars().all()

        for p in perf_records:
            if p.marks_obtained is not None:
                if p.marks_obtained > p.maximum_marks_snapshot:
                    findings.append(
                        AcademicDataQualityFinding(
                            id=uuid.uuid4(),
                            institution_id=institution_id,
                            rule_identifier="PERFORMANCE_MARKS_EXCEED_MAX",
                            entity_type="PERFORMANCE",
                            entity_id=p.id,
                            severity=DataQualitySeverity.CRITICAL.value,
                            description=f"Student performance record has marks ({p.marks_obtained}) higher than assessment maximum ({p.maximum_marks_snapshot}).",
                            source_record={"marks_obtained": p.marks_obtained, "max_marks": p.maximum_marks_snapshot},
                            recommended_action="Audit raw grade sheet and perform audited mark correction.",
                        )
                    )
                elif p.marks_obtained < 0:
                    findings.append(
                        AcademicDataQualityFinding(
                            id=uuid.uuid4(),
                            institution_id=institution_id,
                            rule_identifier="PERFORMANCE_NEGATIVE_MARKS",
                            entity_type="PERFORMANCE",
                            entity_id=p.id,
                            severity=DataQualitySeverity.ERROR.value,
                            description=f"Student performance record has negative marks ({p.marks_obtained}).",
                            source_record={"marks_obtained": p.marks_obtained},
                            recommended_action="Correct negative mark entry.",
                        )
                    )
            elif p.result_status == AssessmentResultStatus.PASSED.value:
                findings.append(
                    AcademicDataQualityFinding(
                        id=uuid.uuid4(),
                        institution_id=institution_id,
                        rule_identifier="PERFORMANCE_PASSED_WITHOUT_MARKS",
                        entity_type="PERFORMANCE",
                        entity_id=p.id,
                        severity=DataQualitySeverity.WARNING.value,
                        description="Record is marked as PASSED, but no numeric marks are recorded.",
                        source_record={"result_status": p.result_status},
                        recommended_action="Verify if assessment was non-graded or enter evaluated numeric marks.",
                    )
                )

        # Rule 4: Check Attendance Records with NOT_RECORDED Status
        att_records = db.execute(
            select(StudentAttendanceRecord).where(StudentAttendanceRecord.institution_id == institution_id)
        ).scalars().all()

        for att in att_records:
            if att.attendance_status == "NOT_RECORDED":
                findings.append(
                    AcademicDataQualityFinding(
                        id=uuid.uuid4(),
                        institution_id=institution_id,
                        rule_identifier="ATTENDANCE_NOT_RECORDED",
                        entity_type="ATTENDANCE",
                        entity_id=att.id,
                        severity=DataQualitySeverity.INFO.value,
                        description=f"Attendance record on {att.attendance_date.strftime('%Y-%m-%d')} for session '{att.session_name}' has status NOT_RECORDED.",
                        source_record={"date": str(att.attendance_date), "session": att.session_name},
                        recommended_action="Update session roster with definitive presence or absence.",
                    )
                )

        for f in findings:
            db.add(f)

        db.commit()
        return findings

    def list_findings(
        self,
        db: Session,
        institution_id: uuid.UUID,
        severity: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> List[AcademicDataQualityFinding]:
        stmt = select(AcademicDataQualityFinding).where(AcademicDataQualityFinding.institution_id == institution_id)
        if severity:
            stmt = stmt.where(AcademicDataQualityFinding.severity == severity)
        if entity_type:
            stmt = stmt.where(AcademicDataQualityFinding.entity_type == entity_type)
        return db.execute(stmt.order_by(AcademicDataQualityFinding.created_at.desc())).scalars().all()

    def resolve_finding(
        self,
        db: Session,
        finding_id: uuid.UUID,
        resolver_id: uuid.UUID,
    ) -> AcademicDataQualityFinding:
        finding = db.get(AcademicDataQualityFinding, finding_id)
        if not finding:
            return None
        finding.resolution_status = "RESOLVED"
        finding.resolved_by = resolver_id
        finding.resolved_at = datetime.now()
        db.commit()
        db.refresh(finding)
        return finding


quality_service = AcademicDataQualityService()
