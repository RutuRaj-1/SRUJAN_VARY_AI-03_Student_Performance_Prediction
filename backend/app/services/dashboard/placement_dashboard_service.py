"""
Placement Officer Dashboard Integration Service (Phase 10).
Aggregates career readiness intelligence, industry role alignments, verified practical projects,
and industry skill gaps.
STRICT DEFENSE-IN-DEPTH: Completely isolated from Academic Risk (Module 06)
and Confidential Academic Interventions (Module 07).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from collections import Counter
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.institution import Institution
from app.models.syllabus import IndustryRoleProfile
from app.models.career import (
    CareerReadinessAnalysis,
    StudentProjectEvidence,
    CareerSkillGapFinding,
)
from app.schemas.dashboard import (
    PlacementOverviewResponse,
    PlacementReadinessDistribution,
    PlacementProjectVerificationSummary,
    SkillGapItem,
    DataFreshnessInfo,
)


class PlacementDashboardService:

    @staticmethod
    def get_placement_overview(
        db: Session,
        institution_id: uuid.UUID,
    ) -> PlacementOverviewResponse:
        """
        Aggregates career readiness intelligence for placement officers.
        Guarantees zero leakage of academic risk or intervention records.
        """
        inst = db.query(Institution).filter(Institution.id == institution_id).first()
        inst_name = inst.name if inst else "Institutional Partner"

        # 1. Role Profiles count
        roles_count = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.is_active == True).count()

        # 2. Evaluated students
        evaluated_students = (
            db.query(CareerReadinessAnalysis.student_id)
            .filter(CareerReadinessAnalysis.institution_id == institution_id)
            .distinct()
            .count()
        )

        # 3. Readiness distribution
        analyses = (
            db.query(CareerReadinessAnalysis)
            .filter(CareerReadinessAnalysis.institution_id == institution_id)
            .all()
        )

        ready_count = sum(1 for a in analyses if a.alignment_status in ("STRONG_EVIDENCE_ALIGNMENT", "READY"))
        approaching_count = sum(1 for a in analyses if a.alignment_status in ("PARTIAL_EVIDENCE_ALIGNMENT", "APPROACHING_READINESS"))
        developing_count = sum(1 for a in analyses if a.alignment_status in ("LIMITED_EVIDENCE_ALIGNMENT", "DEVELOPING"))
        emerging_count = sum(1 for a in analyses if a.alignment_status in ("INSUFFICIENT_EVIDENCE", "EMERGING"))

        readiness_dist = PlacementReadinessDistribution(
            ready_count=ready_count,
            approaching_count=approaching_count,
            developing_count=developing_count,
            emerging_or_unassessed_count=emerging_count,
        )

        # 4. Project verification summary
        verified_projects = (
            db.query(StudentProjectEvidence)
            .filter(
                StudentProjectEvidence.institution_id == institution_id,
                StudentProjectEvidence.verification_status == "VERIFIED"
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

        project_summary = PlacementProjectVerificationSummary(
            verified_projects_count=verified_projects,
            pending_verification_count=pending_projects,
        )

        # 5. Top industry skill gaps
        gaps = (
            db.query(CareerSkillGapFinding)
            .filter(CareerSkillGapFinding.institution_id == institution_id)
            .all()
        )

        gap_counts = Counter((g.competency_name, g.gap_type) for g in gaps)
        top_gaps = [
            SkillGapItem(
                competency_name=comp_name,
                gap_type=gap_type,
                affected_students_count=count,
            )
            for (comp_name, gap_type), count in gap_counts.most_common(5)
        ]

        freshness = DataFreshnessInfo(
            last_updated_at=datetime.now(timezone.utc),
            source_module="Module 08: Career Readiness & Industry Skill Gap Intelligence",
            freshness_status="FRESH",
            is_snapshot=False,
            details="Firewalled career readiness intelligence. Academic risk and intervention data are excluded by design."
        )

        return PlacementOverviewResponse(
            institution_name=inst_name,
            active_role_profiles_count=roles_count,
            total_evaluated_students=evaluated_students,
            readiness_distribution=readiness_dist,
            project_verification_summary=project_summary,
            top_industry_skill_gaps=top_gaps,
            freshness=freshness,
        )


placement_dashboard_service = PlacementDashboardService()
