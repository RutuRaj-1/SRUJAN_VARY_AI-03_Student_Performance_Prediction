"""
Institution Admin Dashboard Integration Service (Phase 10).
Aggregates tenant-level academic intelligence across institutional cohorts:
data quality health, learning mastery attainment rates, risk screening distribution,
intervention lifecycles, and career competency readiness.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.profile import Profile
from app.models.institution import Institution, InstitutionMembership
from app.models.syllabus import AcademicProgram, AcademicSubject
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentAssessmentRecord,
    AcademicDataQualityFinding,
)
from app.models.mastery import TopicMasteryResult
from app.models.risk import AcademicRiskPrediction
from app.models.interventions import AcademicInterventionPlan
from app.models.career import CareerReadinessAnalysis, StudentProjectEvidence
from app.schemas.dashboard import (
    InstitutionOverviewResponse,
    InstitutionSummaryCounts,
    InstitutionAcademicDataStatus,
    InstitutionMasteryOverview,
    InstitutionRiskDistribution,
    InstitutionInterventionMetrics,
    InstitutionCareerReadinessOverview,
    DataFreshnessInfo,
)


class InstitutionDashboardService:

    @staticmethod
    def get_institution_overview(
        db: Session,
        institution_id: uuid.UUID,
    ) -> InstitutionOverviewResponse:
        """
        Aggregates institutional overview metrics for institution administrators.
        Enforces tenant isolation by constraining all sub-queries to institution_id.
        """
        inst = db.query(Institution).filter(Institution.id == institution_id).first()
        if not inst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found."
            )

        # 1. Summary Counts
        total_students = (
            db.query(StudentAcademicProfile)
            .filter(
                StudentAcademicProfile.institution_id == institution_id,
                StudentAcademicProfile.academic_status == "ENROLLED"
            )
            .count()
        )
        total_faculty = (
            db.query(Profile)
            .filter(
                Profile.institution_id == institution_id,
                Profile.role == "FACULTY",
            )
            .count()
        )
        total_programs = (
            db.query(AcademicProgram)
            .filter(AcademicProgram.institution_id == institution_id)
            .count()
        )
        total_subjects = (
            db.query(AcademicSubject)
            .filter(AcademicSubject.institution_id == institution_id)
            .count()
        )

        counts = InstitutionSummaryCounts(
            total_active_students=total_students,
            total_faculty=total_faculty,
            total_programs=total_programs,
            total_subjects=total_subjects,
        )

        # 2. Academic Data Status
        records_q = db.query(StudentAssessmentRecord).filter(StudentAssessmentRecord.institution_id == institution_id)
        total_records = records_q.count()
        verified_count = records_q.filter(StudentAssessmentRecord.verification_status == "VERIFIED").count()
        verified_pct = round((verified_count / total_records) * 100.0, 1) if total_records > 0 else 0.0

        quality_findings = (
            db.query(AcademicDataQualityFinding)
            .filter(
                AcademicDataQualityFinding.institution_id == institution_id,
                AcademicDataQualityFinding.resolution_status == "OPEN"
            )
            .count()
        )

        academic_status = InstitutionAcademicDataStatus(
            total_academic_records=total_records,
            verified_records_pct=verified_pct,
            data_quality_findings_count=quality_findings,
        )

        # 3. Learning Mastery Overview
        mastery_results = db.query(TopicMasteryResult).filter(TopicMasteryResult.institution_id == institution_id).all()
        total_topics = len(mastery_results)
        if total_topics > 0:
            dem_count = sum(1 for m in mastery_results if m.mastery_status == "DEMONSTRATED")
            dev_count = sum(1 for m in mastery_results if m.mastery_status == "DEVELOPING")
            ins_count = sum(1 for m in mastery_results if m.mastery_status == "INSUFFICIENT_EVIDENCE")

            mastery_overview = InstitutionMasteryOverview(
                mastery_demonstrated_pct=round((dem_count / total_topics) * 100.0, 1),
                mastery_developing_pct=round((dev_count / total_topics) * 100.0, 1),
                insufficient_evidence_pct=round((ins_count / total_topics) * 100.0, 1),
                total_evaluated_topics=total_topics,
            )
        else:
            mastery_overview = InstitutionMasteryOverview(
                mastery_demonstrated_pct=0.0,
                mastery_developing_pct=0.0,
                insufficient_evidence_pct=0.0,
                total_evaluated_topics=0,
            )

        # 4. Risk Distribution
        high_risk = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.institution_id == institution_id,
                AcademicRiskPrediction.risk_classification.in_(["HIGH", "CRITICAL"])
            )
            .count()
        )
        med_risk = (
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
        unscreened = max(0, total_students - (high_risk + med_risk + low_risk))

        risk_dist = InstitutionRiskDistribution(
            high_risk_count=high_risk,
            medium_risk_count=med_risk,
            low_risk_count=low_risk,
            unscreened_count=unscreened,
        )

        # 5. Intervention Metrics
        active_plans = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.institution_id == institution_id,
                AcademicInterventionPlan.plan_status == "ACTIVE"
            )
            .count()
        )
        completed_plans = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.institution_id == institution_id,
                AcademicInterventionPlan.plan_status == "COMPLETED"
            )
            .count()
        )
        pending_review = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.institution_id == institution_id,
                AcademicInterventionPlan.plan_status == "PENDING_REVIEW"
            )
            .count()
        )

        intervention_metrics = InstitutionInterventionMetrics(
            active_plans_count=active_plans,
            completed_plans_count=completed_plans,
            pending_review_count=pending_review,
        )

        # 6. Career Readiness Overview
        evaluated_students = (
            db.query(CareerReadinessAnalysis.student_id)
            .filter(CareerReadinessAnalysis.institution_id == institution_id)
            .distinct()
            .count()
        )
        ready_count = (
            db.query(CareerReadinessAnalysis.student_id)
            .filter(
                CareerReadinessAnalysis.institution_id == institution_id,
                CareerReadinessAnalysis.alignment_status.in_(["STRONG_EVIDENCE_ALIGNMENT", "READY"])
            )
            .distinct()
            .count()
        )
        approaching_count = (
            db.query(CareerReadinessAnalysis.student_id)
            .filter(
                CareerReadinessAnalysis.institution_id == institution_id,
                CareerReadinessAnalysis.alignment_status.in_(["PARTIAL_EVIDENCE_ALIGNMENT", "APPROACHING_READINESS"])
            )
            .distinct()
            .count()
        )
        developing_count = (
            db.query(CareerReadinessAnalysis.student_id)
            .filter(
                CareerReadinessAnalysis.institution_id == institution_id,
                CareerReadinessAnalysis.alignment_status.in_(["LIMITED_EVIDENCE_ALIGNMENT", "DEVELOPING"])
            )
            .distinct()
            .count()
        )
        verified_projects = (
            db.query(StudentProjectEvidence)
            .filter(
                StudentProjectEvidence.institution_id == institution_id,
                StudentProjectEvidence.verification_status == "VERIFIED"
            )
            .count()
        )

        career_overview = InstitutionCareerReadinessOverview(
            students_evaluated_count=evaluated_students,
            ready_students_count=ready_count,
            approaching_students_count=approaching_count,
            developing_students_count=developing_count,
            verified_projects_total=verified_projects,
        )

        freshness = DataFreshnessInfo(
            last_updated_at=datetime.utcnow(),
            source_module="Unified Dashboard Integration Layer",
            freshness_status="FRESH",
            is_snapshot=False,
            details=f"Tenant aggregate for {inst.name} ({inst.institution_code})."
        )

        return InstitutionOverviewResponse(
            institution_id=inst.id,
            institution_name=inst.name,
            institution_code=inst.institution_code,
            summary_counts=counts,
            academic_data_status=academic_status,
            mastery_overview=mastery_overview,
            risk_distribution=risk_dist,
            intervention_metrics=intervention_metrics,
            career_readiness_overview=career_overview,
            freshness=freshness,
        )


institution_dashboard_service = InstitutionDashboardService()
