"""
Faculty Dashboard Integration Service (Phase 10).
Aggregates institution- and subject-scoped academic intelligence for authorized faculty members.
Connects verified curriculum, assessment submissions, topic mastery heatmaps,
early academic risk indicators, and intervention review queues.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.profile import Profile
from app.models.institution import Institution
from app.models.syllabus import AcademicSubject
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.mastery import LearningGapFinding
from app.models.risk import AcademicRiskPrediction
from app.models.interventions import AcademicInterventionPlan
from app.models.career import StudentProjectEvidence
from app.schemas.dashboard import (
    FacultyOverviewResponse,
    FacultySubjectItem,
    FacultyVerificationQueue,
    FacultyCohortRiskOverview,
    DataFreshnessInfo,
)


class FacultyDashboardService:

    @staticmethod
    def get_faculty_overview(
        db: Session,
        user_id: uuid.UUID,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
    ) -> FacultyOverviewResponse:
        """
        Aggregates faculty-scoped dashboard metrics across assigned subjects,
        verification queues, academic risk flags, and intervention reviews.
        """
        # 1. Faculty profile and institution
        faculty = db.query(Profile).filter(Profile.id == user_id).first()
        faculty_name = faculty.full_name if faculty else "Faculty Member"

        inst = db.query(Institution).filter(Institution.id == institution_id).first()
        inst_name = inst.name if inst else "Educational Institution"

        # 2. Scope subjects
        subj_query = db.query(AcademicSubject).filter(AcademicSubject.institution_id == institution_id)
        if subject_id:
            subj_query = subj_query.filter(AcademicSubject.id == subject_id)
        subjects = subj_query.all()

        subject_items: List[FacultySubjectItem] = []
        monitored_student_ids = set()

        for s in subjects:
            enrollments = (
                db.query(StudentSubjectEnrollment)
                .filter(
                    StudentSubjectEnrollment.subject_id == s.id,
                    StudentSubjectEnrollment.enrollment_status == "ACTIVE"
                )
                .all()
            )
            for enr in enrollments:
                monitored_student_ids.add(enr.student_id)

            # Average attendance for subject
            att_records = (
                db.query(StudentAttendanceRecord)
                .filter(StudentAttendanceRecord.subject_id == s.id)
                .all()
            )
            if att_records:
                present_count = sum(1 for a in att_records if a.attendance_status in ("PRESENT", "LATE"))
                avg_att = round((present_count / len(att_records)) * 100.0, 1)
            else:
                avg_att = None

            # Average marks for subject
            assessments = db.query(AcademicAssessment).filter(AcademicAssessment.subject_id == s.id).all()
            ass_ids = [a.id for a in assessments]
            if ass_ids:
                records = (
                    db.query(StudentAssessmentRecord)
                    .filter(
                        StudentAssessmentRecord.assessment_id.in_(ass_ids),
                        StudentAssessmentRecord.verification_status == "VERIFIED",
                        StudentAssessmentRecord.marks_obtained.isnot(None),
                        StudentAssessmentRecord.maximum_marks_snapshot > 0
                    )
                    .all()
                )
                if records:
                    avg_m = round(
                        sum((r.marks_obtained / r.maximum_marks_snapshot) * 100.0 for r in records) / len(records),
                        1
                    )
                else:
                    avg_m = None
            else:
                avg_m = None

            subject_items.append(
                FacultySubjectItem(
                    subject_id=s.id,
                    code=s.code,
                    name=s.name,
                    semester=s.semester,
                    enrolled_students_count=len(enrollments),
                    average_attendance=avg_att,
                    average_marks=avg_m,
                )
            )

        # 3. Verification Queue
        pending_academic = (
            db.query(StudentAssessmentRecord)
            .filter(
                StudentAssessmentRecord.institution_id == institution_id,
                StudentAssessmentRecord.verification_status != "VERIFIED"
            )
            .count()
        )
        pending_interventions = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.institution_id == institution_id,
                AcademicInterventionPlan.plan_status == "PENDING_REVIEW"
            )
            .count()
        )
        pending_projects = (
            db.query(StudentProjectEvidence)
            .filter(
                StudentProjectEvidence.institution_id == institution_id,
                StudentProjectEvidence.verification_status == "PENDING_REVIEW"
            )
            .count()
        )

        verification_queue = FacultyVerificationQueue(
            pending_academic_records=pending_academic,
            pending_interventions_review=pending_interventions,
            pending_practical_projects=pending_projects,
        )

        # 4. Cohort Risk Overview
        high_risk = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.institution_id == institution_id,
                AcademicRiskPrediction.risk_classification.in_(["HIGH", "CRITICAL"])
            )
            .count()
        )
        mod_risk = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.institution_id == institution_id,
                AcademicRiskPrediction.risk_classification == "MODERATE"
            )
            .count()
        )
        low_risk = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.institution_id == institution_id,
                AcademicRiskPrediction.risk_classification == "LOW"
            )
            .count()
        )

        learning_gaps = (
            db.query(LearningGapFinding)
            .filter(
                LearningGapFinding.institution_id == institution_id,
                LearningGapFinding.status == "OPEN"
            )
            .count()
        )

        active_interventions = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.institution_id == institution_id,
                AcademicInterventionPlan.plan_status == "ACTIVE"
            )
            .count()
        )

        cohort_risk = FacultyCohortRiskOverview(
            high_risk_students_count=high_risk,
            moderate_risk_students_count=mod_risk,
            low_risk_students_count=low_risk,
            learning_gaps_flagged_count=learning_gaps,
            active_interventions_count=active_interventions,
        )

        freshness = DataFreshnessInfo(
            last_updated_at=datetime.utcnow(),
            source_module="Unified Dashboard Integration Layer",
            freshness_status="FRESH",
            is_snapshot=False,
            details=f"Monitoring {len(monitored_student_ids)} students across {len(subjects)} subjects."
        )

        return FacultyOverviewResponse(
            faculty_name=faculty_name,
            institution_name=inst_name,
            department="Computer Science & Engineering",
            assigned_subjects=subject_items,
            total_students_monitored=len(monitored_student_ids),
            verification_queue=verification_queue,
            cohort_risk_overview=cohort_risk,
            freshness=freshness,
        )


faculty_dashboard_service = FacultyDashboardService()
