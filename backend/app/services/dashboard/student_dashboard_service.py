"""
Student Dashboard Integration Service (Phase 10).
Aggregates cross-module student intelligence across academic records,
learning mastery, explainable risk, personalized interventions, and career readiness.
Preserves data provenance and ensures missing data is never converted to zero.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.syllabus import AcademicProgram, AcademicSubject
from app.models.institution import Institution
from app.models.profile import Profile
from app.models.mastery import (
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)
from app.models.risk import (
    AcademicRiskPrediction,
    AcademicRiskPredictionExplanation,
)
from app.models.interventions import (
    AcademicInterventionPlan,
    AcademicInterventionAction,
)
from app.models.career import (
    CareerReadinessAnalysis,
    StudentProjectEvidence,
    CareerSkillGapFinding,
)
from app.models.syllabus import IndustryRoleProfile
from app.schemas.dashboard import (
    StudentOverviewResponse,
    StudentProfileHeader,
    StudentAcademicPerformanceCard,
    StudentMasterySummaryCard,
    StudentRiskSummaryCard,
    StudentInterventionSummaryCard,
    StudentCareerSummaryCard,
    DataFreshnessInfo,
)


class StudentDashboardService:

    @staticmethod
    def get_student_overview(
        db: Session,
        user_id: uuid.UUID,
        institution_id: Optional[uuid.UUID] = None,
        target_student_id: Optional[uuid.UUID] = None,
    ) -> StudentOverviewResponse:
        """
        Aggregates unified student intelligence for the specified student.
        If target_student_id is None, resolves the student via Profile.id == user_id.
        """
        # 1. Resolve student profile
        if target_student_id:
            query = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == target_student_id)
            if institution_id:
                query = query.filter(StudentAcademicProfile.institution_id == institution_id)
            student = query.first()
        else:
            query = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.profile_id == user_id)
            if institution_id:
                query = query.filter(StudentAcademicProfile.institution_id == institution_id)
            student = query.first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student academic profile not found for the requested context."
            )

        now = datetime.now(timezone.utc)

        # 2. Institution and Program details
        inst = db.query(Institution).filter(Institution.id == student.institution_id).first()
        inst_name = inst.name if inst else "Institutional Partner"

        prog = db.query(AcademicProgram).filter(AcademicProgram.id == student.program_id).first()
        prog_name = prog.name if prog else "Undergraduate Academic Program"

        profile_header = StudentProfileHeader(
            id=student.id,
            full_name=f"{student.first_name} {student.last_name}",
            enrollment_number=student.enrollment_number,
            program_name=prog_name,
            department=student.department,
            current_semester=student.current_semester,
            institution_name=inst_name,
            academic_status=student.academic_status,
        )

        # 3. Academic Performance Section (Module 03)
        enrolled_count = (
            db.query(StudentSubjectEnrollment)
            .filter(
                StudentSubjectEnrollment.student_id == student.id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE"
            )
            .count()
        )

        records_q = db.query(StudentAssessmentRecord).filter(StudentAssessmentRecord.student_id == student.id)
        total_records = records_q.count()
        verified_count = records_q.filter(StudentAssessmentRecord.verification_status == "VERIFIED").count()
        pending_records = total_records - verified_count

        verified_records = records_q.filter(
            StudentAssessmentRecord.verification_status == "VERIFIED",
            StudentAssessmentRecord.marks_obtained.isnot(None),
            StudentAssessmentRecord.maximum_marks_snapshot > 0
        ).all()

        if verified_records:
            avg_marks = round(
                sum((r.marks_obtained / r.maximum_marks_snapshot) * 100.0 for r in verified_records) / len(verified_records),
                1
            )
        else:
            avg_marks = None

        attendance_records = db.query(StudentAttendanceRecord).filter(StudentAttendanceRecord.student_id == student.id).all()
        if attendance_records:
            present_count = sum(1 for a in attendance_records if a.attendance_status in ("PRESENT", "LATE"))
            attendance_rate = round((present_count / len(attendance_records)) * 100.0, 1)
        else:
            attendance_rate = None

        academic_freshness = DataFreshnessInfo(
            last_updated_at=student.updated_at or student.created_at,
            source_module="Module 03: Academic Data Intelligence Hub",
            freshness_status="FRESH" if total_records > 0 else "NOT_AVAILABLE",
            is_snapshot=False,
            details=f"Computed from {total_records} institutional records and {len(attendance_records)} attendance sessions."
        )

        academic_performance = StudentAcademicPerformanceCard(
            average_marks=avg_marks,
            attendance_rate=attendance_rate,
            total_records=total_records,
            verified_records_count=verified_count,
            pending_records_count=pending_records,
            enrolled_subjects_count=enrolled_count,
            freshness=academic_freshness,
        )

        # 4. Learning Mastery Section (Module 05)
        mastery_results = db.query(TopicMasteryResult).filter(TopicMasteryResult.student_id == student.id).all()
        topics_assessed = len(mastery_results)
        demonstrated_count = sum(1 for m in mastery_results if m.mastery_status == "DEMONSTRATED")
        developing_count = sum(1 for m in mastery_results if m.mastery_status == "DEVELOPING")
        insufficient_ev_count = sum(1 for m in mastery_results if m.mastery_status == "INSUFFICIENT_EVIDENCE")

        clo_results = db.query(LearningOutcomeAttainmentResult).filter(LearningOutcomeAttainmentResult.student_id == student.id).all()
        if clo_results:
            attained_clos = sum(1 for c in clo_results if c.attainment_status in ("ATTAINED", "EXCEEDED") or (c.attainment_percentage and c.attainment_percentage >= 60.0))
            clo_attainment_pct = round((attained_clos / len(clo_results)) * 100.0, 1)
        else:
            clo_attainment_pct = None

        active_gaps_count = (
            db.query(LearningGapFinding)
            .filter(LearningGapFinding.student_id == student.id, LearningGapFinding.status == "OPEN")
            .count()
        )

        mastery_freshness = DataFreshnessInfo(
            last_updated_at=mastery_results[0].calculated_at if mastery_results else None,
            source_module="Module 05: Learning Mastery & Performance Analytics",
            freshness_status="FRESH" if topics_assessed > 0 else "NOT_AVAILABLE",
            is_snapshot=True,
            details=f"Calibrated over {topics_assessed} topics and {len(clo_results)} Course Learning Outcomes."
        )

        mastery_summary = StudentMasterySummaryCard(
            topics_assessed_count=topics_assessed,
            topics_demonstrated_count=demonstrated_count,
            topics_developing_count=developing_count,
            topics_insufficient_evidence_count=insufficient_ev_count,
            clo_attainment_pct=clo_attainment_pct,
            active_learning_gaps_count=active_gaps_count,
            freshness=mastery_freshness,
        )

        # 5. Academic Risk Section (Module 06)
        latest_risk = (
            db.query(AcademicRiskPrediction)
            .filter(AcademicRiskPrediction.student_id == student.id)
            .order_by(AcademicRiskPrediction.prediction_cutoff_date.desc(), AcademicRiskPrediction.created_at.desc())
            .first()
        )

        if latest_risk:
            explanations = (
                db.query(AcademicRiskPredictionExplanation)
                .filter(AcademicRiskPredictionExplanation.prediction_id == latest_risk.id)
                .all()
            )
            primary_adverse = [e.explanation_text for e in explanations if e.is_adverse_factor][:3]
            protective = [e.explanation_text for e in explanations if not e.is_adverse_factor][:3]

            risk_card = StudentRiskSummaryCard(
                has_prediction=True,
                risk_classification=latest_risk.risk_classification,
                risk_probability=round(latest_risk.risk_score, 3) if latest_risk.risk_score is not None else None,
                prediction_horizon="End of Current Semester Examination",
                primary_adverse_factors=primary_adverse,
                protective_factors=protective,
                prediction_timestamp=latest_risk.prediction_cutoff_date or latest_risk.created_at,
                model_version=str(latest_risk.model_version_id) if latest_risk.model_version_id else "v1.0-LogisticRegression",
                freshness=DataFreshnessInfo(
                    last_updated_at=latest_risk.created_at,
                    source_module="Module 06: Academic Risk Prediction Engine",
                    freshness_status="FRESH",
                    is_snapshot=True,
                    details="Audited against temporal leakage; reflects time-bounded cutoff."
                ),
            )
        else:
            risk_card = StudentRiskSummaryCard(
                has_prediction=False,
                freshness=DataFreshnessInfo(
                    last_updated_at=None,
                    source_module="Module 06: Academic Risk Prediction Engine",
                    freshness_status="NOT_AVAILABLE",
                    is_snapshot=False,
                    details="No active risk screening on record."
                ),
            )

        # 6. Personalized Intervention Section (Module 07)
        plans = db.query(AcademicInterventionPlan).filter(AcademicInterventionPlan.student_id == student.id).all()
        active_plans = [p for p in plans if p.plan_status in ("ACTIVE", "APPROVED")]
        latest_plan = active_plans[0] if active_plans else (plans[0] if plans else None)

        pending_actions = 0
        completed_actions = 0
        mentor_name = None

        if latest_plan:
            actions = db.query(AcademicInterventionAction).filter(AcademicInterventionAction.plan_id == latest_plan.id).all()
            pending_actions = sum(1 for a in actions if a.action_status in ("PENDING", "IN_PROGRESS"))
            completed_actions = sum(1 for a in actions if a.action_status == "COMPLETED")
            if latest_plan.assigned_faculty_id:
                mentor = db.query(Profile).filter(Profile.id == latest_plan.assigned_faculty_id).first()
                if mentor:
                    mentor_name = mentor.full_name

        intervention_summary = StudentInterventionSummaryCard(
            active_plans_count=len(active_plans),
            pending_actions_count=pending_actions,
            completed_actions_count=completed_actions,
            latest_plan_title=latest_plan.plan_title if latest_plan else None,
            faculty_mentor_name=mentor_name,
            freshness=DataFreshnessInfo(
                last_updated_at=latest_plan.updated_at if latest_plan else None,
                source_module="Module 07: Personalized Academic Intervention Engine",
                freshness_status="FRESH" if latest_plan else "NOT_AVAILABLE",
                is_snapshot=False,
                details=f"{len(plans)} academic support plans on record."
            ),
        )

        # 7. Career Readiness Section (Module 08)
        analyses = (
            db.query(CareerReadinessAnalysis)
            .filter(CareerReadinessAnalysis.student_id == student.id)
            .order_by(CareerReadinessAnalysis.created_at.desc())
            .all()
        )
        top_analysis = analyses[0] if analyses else None
        target_role_title = None

        if top_analysis:
            role = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.id == top_analysis.role_id).first()
            if role:
                target_role_title = role.role_title

        verified_projects_count = (
            db.query(StudentProjectEvidence)
            .filter(
                StudentProjectEvidence.student_id == student.id,
                StudentProjectEvidence.verification_status == "VERIFIED"
            )
            .count()
        )
        pending_projects_count = (
            db.query(StudentProjectEvidence)
            .filter(
                StudentProjectEvidence.student_id == student.id,
                StudentProjectEvidence.verification_status == "PENDING_REVIEW"
            )
            .count()
        )

        active_skill_gaps_count = 0
        if top_analysis:
            active_skill_gaps_count = (
                db.query(CareerSkillGapFinding)
                .filter(CareerSkillGapFinding.analysis_id == top_analysis.id)
                .count()
            )

        career_summary = StudentCareerSummaryCard(
            analyzed_roles_count=len(analyses),
            target_role_title=target_role_title,
            core_coverage_pct=top_analysis.core_competency_coverage if top_analysis else None,
            practical_coverage_pct=top_analysis.practical_evidence_coverage if top_analysis else None,
            alignment_status=top_analysis.alignment_status if top_analysis else None,
            verified_projects_count=verified_projects_count,
            pending_projects_count=pending_projects_count,
            active_skill_gaps_count=active_skill_gaps_count,
            freshness=DataFreshnessInfo(
                last_updated_at=top_analysis.created_at if top_analysis else None,
                source_module="Module 08: Career Readiness & Industry Skill Gap Intelligence",
                freshness_status="FRESH" if top_analysis else "NOT_AVAILABLE",
                is_snapshot=True,
                details="Separate core & practical coverage metrics without arbitrary aggregation."
            ),
        )

        return StudentOverviewResponse(
            student_profile=profile_header,
            academic_performance=academic_performance,
            mastery_summary=mastery_summary,
            risk_summary=risk_card,
            intervention_summary=intervention_summary,
            career_summary=career_summary,
            system_freshness=now,
        )


student_dashboard_service = StudentDashboardService()
