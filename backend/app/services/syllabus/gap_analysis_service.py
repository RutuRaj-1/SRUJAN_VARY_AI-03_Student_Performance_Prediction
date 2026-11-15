import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.enums import IndustryMappingStatus
from app.models.syllabus import (
    CurriculumGapAnalysis,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
    Competency,
)
from app.schemas.syllabus import (
    GapAnalysisSummaryResponse,
    CurriculumGapAnalysisResponse,
)


class GapAnalysisService:
    def get_gap_summaries_for_subject(
        self,
        db: Session,
        subject_id: uuid.UUID,
    ) -> List[GapAnalysisSummaryResponse]:
        # Fetch all roles
        roles = db.execute(select(IndustryRoleProfile)).scalars().all()
        summaries = []

        for role in roles:
            # Query gap analyses for this role and subject
            stmt = (
                select(CurriculumGapAnalysis, IndustryCompetencyRequirement, Competency)
                .join(
                    IndustryCompetencyRequirement,
                    CurriculumGapAnalysis.industry_competency_id == IndustryCompetencyRequirement.id,
                )
                .outerjoin(
                    Competency,
                    CurriculumGapAnalysis.academic_competency_id == Competency.id,
                )
                .where(
                    CurriculumGapAnalysis.subject_id == subject_id,
                    CurriculumGapAnalysis.role_id == role.id,
                )
            )
            results = db.execute(stmt).all()

            if not results:
                continue

            total = len(results)
            direct_cnt = 0
            partial_cnt = 0
            missing_cnt = 0
            outdated_cnt = 0
            gap_items: List[CurriculumGapAnalysisResponse] = []

            for gap_analysis, req, comp in results:
                status_val = gap_analysis.status
                if status_val == IndustryMappingStatus.DIRECT.value:
                    direct_cnt += 1
                elif status_val == IndustryMappingStatus.PARTIAL.value:
                    partial_cnt += 1
                elif status_val == IndustryMappingStatus.OUTDATED.value:
                    outdated_cnt += 1
                else:
                    missing_cnt += 1

                gap_items.append(
                    CurriculumGapAnalysisResponse(
                        id=gap_analysis.id,
                        subject_id=gap_analysis.subject_id,
                        role_id=gap_analysis.role_id,
                        role_title=role.role_title,
                        industry_competency_id=req.id,
                        industry_competency_name=req.competency_name,
                        category=req.category,
                        required_depth=req.required_depth,
                        importance=req.importance,
                        academic_competency_id=comp.id if comp else None,
                        academic_competency_name=comp.title if comp else None,
                        status=gap_analysis.status,
                        rationale=gap_analysis.rationale,
                        evidence=gap_analysis.evidence,
                        recommendation=gap_analysis.recommendation,
                        analyzed_at=gap_analysis.analyzed_at,
                    )
                )

            coverage_pct = round(((direct_cnt * 1.0 + partial_cnt * 0.5) / max(total, 1)) * 100.0, 1)

            summaries.append(
                GapAnalysisSummaryResponse(
                    subject_id=subject_id,
                    role_id=role.id,
                    role_title=role.role_title,
                    total_industry_requirements=total,
                    direct_match_count=direct_cnt,
                    partial_match_count=partial_cnt,
                    missing_count=missing_cnt,
                    outdated_count=outdated_cnt,
                    coverage_percentage=coverage_pct,
                    gaps=gap_items,
                )
            )

        return summaries


gap_analysis_service = GapAnalysisService()
