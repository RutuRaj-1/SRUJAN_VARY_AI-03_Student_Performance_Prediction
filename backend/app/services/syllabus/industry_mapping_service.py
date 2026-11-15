import uuid
import re
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.enums import IndustryMappingStatus
from app.models.syllabus import (
    AcademicSubject,
    Competency,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
    CurriculumGapAnalysis,
)


def compute_text_similarity_overlap(req_title: str, comp_title: str) -> float:
    def tokenize(s: str):
        return set(re.findall(r"\b[a-zA-Z]{3,}\b", s.lower()))

    tokens_req = tokenize(req_title)
    tokens_comp = tokenize(comp_title)

    if not tokens_req or not tokens_comp:
        return 0.0

    common = tokens_req.intersection(tokens_comp)
    return len(common) / len(tokens_req)


class IndustryMappingService:
    def map_subject_to_roles(
        self,
        db: Session,
        subject: AcademicSubject,
        competencies: List[Competency],
    ) -> List[CurriculumGapAnalysis]:
        # Delete old analyses for this subject to ensure fresh, accurate results
        db.query(CurriculumGapAnalysis).filter(CurriculumGapAnalysis.subject_id == subject.id).delete()

        # Load all industry roles and their requirements
        roles_stmt = select(IndustryRoleProfile)
        roles = db.execute(roles_stmt).scalars().all()

        analyses = []

        for role in roles:
            # Query requirements for this role
            reqs_stmt = select(IndustryCompetencyRequirement).where(
                IndustryCompetencyRequirement.role_id == role.id
            )
            requirements = db.execute(reqs_stmt).scalars().all()

            for req in requirements:
                best_match: Optional[Competency] = None
                best_score: float = 0.0

                for comp in competencies:
                    score = compute_text_similarity_overlap(req.competency_name, comp.title)
                    # Also check description overlap
                    if score < 0.3 and comp.description:
                        desc_score = compute_text_similarity_overlap(req.competency_name, comp.description)
                        score = max(score, desc_score * 0.8)

                    if score > best_score:
                        best_score = score
                        best_match = comp

                # Determine status and rationale
                if best_score >= 0.5 and best_match:
                    if best_match.depth_level >= req.required_depth:
                        status = IndustryMappingStatus.DIRECT
                        rationale = f"Direct alignment: '{best_match.title}' thoroughly satisfies industry requirement at depth {best_match.depth_level}/{req.required_depth}."
                        recommendation = "Maintain current rigorous curriculum outcomes and practical labs."
                    else:
                        status = IndustryMappingStatus.PARTIAL
                        rationale = f"Partial alignment: Syllabus addresses '{best_match.title}' conceptually (depth {best_match.depth_level}), but falls short of industry requirement (depth {req.required_depth})."
                        recommendation = f"Introduce advanced hands-on lab exercises or mini-projects targeting {req.competency_name}."
                elif best_score >= 0.2 and best_match:
                    status = IndustryMappingStatus.PARTIAL
                    rationale = f"Conceptual basis partially touched in '{best_match.title}', but explicit industry depth is not covered."
                    recommendation = f"Upgrade unit curriculum to integrate current industry patterns for {req.competency_name}."
                else:
                    status = IndustryMappingStatus.MISSING
                    rationale = f"Curriculum gap: '{req.competency_name}' is not addressed in this subject's syllabus."
                    recommendation = f"Add elective module, supplemental workshop, or dedicated laboratory course covering {req.competency_name}."

                gap_record = CurriculumGapAnalysis(
                    id=uuid.uuid4(),
                    subject_id=subject.id,
                    role_id=role.id,
                    industry_competency_id=req.id,
                    academic_competency_id=best_match.id if best_match else None,
                    status=status.value,
                    rationale=rationale,
                    evidence=best_match.syllabus_evidence if best_match else "No matching syllabus topic identified.",
                    recommendation=recommendation,
                )
                db.add(gap_record)
                analyses.append(gap_record)

        db.flush()
        return analyses


industry_mapping_service = IndustryMappingService()
