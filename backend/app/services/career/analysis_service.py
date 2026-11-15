import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.career import (
    CareerReadinessAnalysis,
    CareerSkillGapFinding,
    CareerDevelopmentRecommendation,
    StudentCompetencyEvidence,
    StudentProjectEvidence,
    DEFAULT_CAREER_READINESS_DISCLAIMER,
)
from app.models.syllabus import (
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
    Competency,
    AcademicSubject,
    SubjectCompetencyMapping,
)
from app.models.academic_data import StudentAcademicProfile
from app.models.interventions import AcademicInterventionPlan
from app.models.enums import (
    CompetencyEvidenceState,
    CompetencyEvidenceType,
    CareerAlignmentStatus,
    CareerSkillGapType,
    CareerGapSeverity,
    CareerRecommendationType,
    CareerRecommendationStatus,
    RoleRequirementImportance,
    RoleMappingStatus,
    ProjectVerificationStatus,
)
from app.services.career.evidence_service import CompetencyEvidenceService


class CareerReadinessAnalysisService:
    @staticmethod
    def _matches_competency(req_name: str, ev_name: str) -> bool:
        r = req_name.strip().lower()
        e = ev_name.strip().lower()
        if r == e or r in e or e in r:
            return True
        # Keyword token overlap (e.g. "database", "python", "algorithms")
        r_tokens = set(r.replace('&', ' ').replace('/', ' ').replace('-', ' ').split())
        e_tokens = set(e.replace('&', ' ').replace('/', ' ').replace('-', ' ').split())
        meaningful = {t for t in r_tokens if len(t) > 3}
        return len(meaningful.intersection(e_tokens)) > 0

    @staticmethod
    def analyze_role_readiness(
        db: Session,
        student_id: uuid.UUID,
        role_id: uuid.UUID,
        institution_id: uuid.UUID,
        force_recalculate: bool = False,
    ) -> CareerReadinessAnalysis:
        """
        Executes a role-specific deterministic career readiness analysis comparing
        approved industry role requirements against verified student competency evidence.
        """
        # 1. Fetch role and its requirements
        role = db.query(IndustryRoleProfile).options(
            joinedload(IndustryRoleProfile.requirements)
        ).filter(IndustryRoleProfile.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Industry role profile '{role_id}' not found.",
            )

        # 2. Check for recent existing analysis if not forced
        if not force_recalculate:
            existing = db.query(CareerReadinessAnalysis).options(
                joinedload(CareerReadinessAnalysis.gap_findings),
                joinedload(CareerReadinessAnalysis.recommendations),
            ).filter(
                CareerReadinessAnalysis.student_id == student_id,
                CareerReadinessAnalysis.role_id == role_id,
            ).order_by(CareerReadinessAnalysis.created_at.desc()).first()
            if existing:
                return existing

        # 3. Retrieve student competency evidence
        evidence_list = CompetencyEvidenceService.get_student_evidence(db, student_id, institution_id)

        # 4. Also check verified student projects for practical coverage
        verified_projects = db.query(StudentProjectEvidence).filter(
            StudentProjectEvidence.student_id == student_id,
            StudentProjectEvidence.verification_status == ProjectVerificationStatus.VERIFIED.value,
        ).all()

        # 5. Evaluate each requirement
        requirements = role.requirements or []
        total_reqs = len(requirements)
        if total_reqs == 0:
            total_reqs = 1  # Avoid division by zero

        demonstrated_count = 0
        developing_count = 0
        insufficient_evidence_count = 0
        not_assessed_count = 0
        review_required_count = 0
        faculty_reviewed_count = 0

        core_reqs_total = 0
        core_reqs_met = 0
        practical_reqs_total = 0
        practical_reqs_met = 0

        gaps_to_create: List[Dict[str, Any]] = []

        for req in requirements:
            is_core = req.importance in (RoleRequirementImportance.CORE.value, "HIGH")
            is_practical = req.category in ("PROGRAMMING", "PRACTICAL", "TOOLS_TECHNOLOGIES")
            if is_core:
                core_reqs_total += 1
            if is_practical:
                practical_reqs_total += 1

            # Check if mapping is unapproved
            if req.mapping_status in (RoleMappingStatus.AI_SUGGESTED.value, RoleMappingStatus.FACULTY_REVIEW_REQUIRED.value):
                review_required_count += 1
                gaps_to_create.append({
                    "requirement_id": req.id,
                    "competency_name": req.competency_name,
                    "importance": req.importance,
                    "gap_type": CareerSkillGapType.MAPPING_GAP.value,
                    "current_evidence_state": CompetencyEvidenceState.REVIEW_REQUIRED.value,
                    "gap_severity": CareerGapSeverity.LOW.value,
                    "rationale": f"Competency requirement '{req.competency_name}' is currently {req.mapping_status} and requires faculty review.",
                    "suggested_action": "Faculty review and approval of the role requirement mapping.",
                    "evidence_needed": "Authorized faculty confirmation of industry benchmark relevancy.",
                })
                continue

            # Find matching student evidence
            matched_evidence = [
                ev for ev in evidence_list
                if CareerReadinessAnalysisService._matches_competency(req.competency_name, ev.competency_name)
            ]

            if matched_evidence:
                # Prioritize: DEMONSTRATED > DEVELOPING > REVIEW_REQUIRED > INSUFFICIENT_EVIDENCE
                best_ev = matched_evidence[0]
                for ev in matched_evidence:
                    if ev.evidence_state == CompetencyEvidenceState.DEMONSTRATED.value:
                        best_ev = ev
                        break
                    elif ev.evidence_state == CompetencyEvidenceState.DEVELOPING.value and best_ev.evidence_state != CompetencyEvidenceState.DEMONSTRATED.value:
                        best_ev = ev

                if best_ev.verified_by is not None:
                    faculty_reviewed_count += 1

                if best_ev.evidence_state == CompetencyEvidenceState.DEMONSTRATED.value:
                    demonstrated_count += 1
                    if is_core:
                        core_reqs_met += 1
                    if is_practical:
                        # Check if practical project or just theoretical exam
                        has_practical = any(ev.evidence_type == CompetencyEvidenceType.PROJECT_DEMONSTRATION.value for ev in matched_evidence)
                        if has_practical:
                            practical_reqs_met += 1
                        else:
                            # Theoretical demonstrated but practical project gap
                            gaps_to_create.append({
                                "requirement_id": req.id,
                                "competency_name": req.competency_name,
                                "importance": req.importance,
                                "gap_type": CareerSkillGapType.PRACTICAL_EVIDENCE_GAP.value,
                                "current_evidence_state": CompetencyEvidenceState.DEMONSTRATED.value,
                                "gap_severity": CareerGapSeverity.MODERATE.value,
                                "rationale": f"Demonstrated conceptual mastery in academic assessments, but lacks verified practical code or project evidence.",
                                "suggested_action": f"Build a hands-on project demonstrating {req.competency_name} and submit for faculty review.",
                                "evidence_needed": "Verified repository or lab submission.",
                            })
                elif best_ev.evidence_state == CompetencyEvidenceState.DEVELOPING.value:
                    developing_count += 1
                    if is_core:
                        core_reqs_met += 1
                    gaps_to_create.append({
                        "requirement_id": req.id,
                        "competency_name": req.competency_name,
                        "importance": req.importance,
                        "gap_type": CareerSkillGapType.DEMONSTRATED_GAP.value,
                        "current_evidence_state": CompetencyEvidenceState.DEVELOPING.value,
                        "gap_severity": CareerGapSeverity.HIGH.value if is_core else CareerGapSeverity.MODERATE.value,
                        "rationale": f"Developing proficiency observed ({best_ev.score_or_metric or 50:.1f}%), but does not yet reach the required {req.required_depth}/5 depth benchmark.",
                        "suggested_action": f"Complete targeted exercises and problem sets on {req.competency_name}.",
                        "evidence_needed": "Continuous assessment score >= 70% or practical coding verification.",
                    })
                elif best_ev.evidence_state == CompetencyEvidenceState.REVIEW_REQUIRED.value:
                    review_required_count += 1
                elif best_ev.evidence_state == CompetencyEvidenceState.INSUFFICIENT_EVIDENCE.value:
                    insufficient_evidence_count += 1
                    gaps_to_create.append({
                        "requirement_id": req.id,
                        "competency_name": req.competency_name,
                        "importance": req.importance,
                        "gap_type": CareerSkillGapType.EVIDENCE_GAP.value,
                        "current_evidence_state": CompetencyEvidenceState.INSUFFICIENT_EVIDENCE.value,
                        "gap_severity": CareerGapSeverity.HIGH.value if is_core else CareerGapSeverity.MODERATE.value,
                        "rationale": f"Insufficient verified evidence available to conclude competency standing.",
                        "suggested_action": f"Take formative diagnostic assessment or complete laboratory task.",
                        "evidence_needed": "At least one evaluated assessment or verified project submission.",
                    })
                else:
                    not_assessed_count += 1
                    gaps_to_create.append({
                        "requirement_id": req.id,
                        "competency_name": req.competency_name,
                        "importance": req.importance,
                        "gap_type": CareerSkillGapType.DEMONSTRATED_GAP.value,
                        "current_evidence_state": CompetencyEvidenceState.NOT_YET_DEMONSTRATED.value,
                        "gap_severity": CareerGapSeverity.HIGH.value if is_core else CareerGapSeverity.MODERATE.value,
                        "rationale": f"Evaluations exist, but student has not demonstrated required threshold ({best_ev.score_or_metric or 0:.1f}%).",
                        "suggested_action": f"Engage in revision modules and retake topic evaluation.",
                        "evidence_needed": "Demonstrated assessment score >= 70%.",
                    })
            else:
                # No evidence exists at all
                not_assessed_count += 1
                gaps_to_create.append({
                    "requirement_id": req.id,
                    "competency_name": req.competency_name,
                    "importance": req.importance,
                    "gap_type": CareerSkillGapType.EVIDENCE_GAP.value,
                    "current_evidence_state": CompetencyEvidenceState.NOT_ASSESSED.value,
                    "gap_severity": CareerGapSeverity.HIGH.value if is_core else CareerGapSeverity.LOW.value,
                    "rationale": f"No academic assessments, topic masteries, or practical submissions found for '{req.competency_name}'.",
                    "suggested_action": f"Enroll in relevant coursework or complete an independent practical project.",
                    "evidence_needed": "Course enrollment completion, assessment attempt, or project portfolio submission.",
                })

        # Calculate coverage percentages
        core_coverage = (core_reqs_met / core_reqs_total * 100.0) if core_reqs_total > 0 else 0.0
        practical_coverage = (practical_reqs_met / practical_reqs_total * 100.0) if practical_reqs_total > 0 else 0.0

        # Calculate alignment status
        if core_coverage >= 70.0 and practical_coverage >= 50.0:
            alignment = CareerAlignmentStatus.STRONG_EVIDENCE_ALIGNMENT.value
            rationale = (
                f"Student demonstrates strong evidence alignment ({core_coverage:.1f}% core coverage, "
                f"{practical_coverage:.1f}% practical coverage) across {role.role_title} requirements."
            )
        elif (demonstrated_count + developing_count) >= (total_reqs * 0.40):
            alignment = CareerAlignmentStatus.PARTIAL_EVIDENCE_ALIGNMENT.value
            rationale = (
                f"Student exhibits partial evidence alignment with {demonstrated_count} demonstrated and "
                f"{developing_count} developing competencies. Practical evidence coverage is {practical_coverage:.1f}%."
            )
        elif demonstrated_count > 0:
            alignment = CareerAlignmentStatus.LIMITED_EVIDENCE_ALIGNMENT.value
            rationale = (
                f"Limited verified evidence currently aligns with {role.role_title}. "
                f"Core competency coverage is {core_coverage:.1f}%."
            )
        else:
            alignment = CareerAlignmentStatus.INSUFFICIENT_EVIDENCE.value
            rationale = (
                f"Insufficient academic and practical evidence exists to evaluate readiness for {role.role_title}. "
                f"{not_assessed_count} requirements have not yet been assessed."
            )

        # 6. Create CareerReadinessAnalysis record
        analysis = CareerReadinessAnalysis(
            institution_id=institution_id,
            student_id=student_id,
            role_id=role_id,
            alignment_status=alignment,
            total_requirements_count=total_reqs,
            demonstrated_count=demonstrated_count,
            developing_count=developing_count,
            insufficient_evidence_count=insufficient_evidence_count,
            not_assessed_count=not_assessed_count,
            review_required_count=review_required_count,
            core_competency_coverage=round(core_coverage, 1),
            practical_evidence_coverage=round(practical_coverage, 1),
            faculty_reviewed_count=faculty_reviewed_count,
            summary_rationale=rationale,
            disclaimer=DEFAULT_CAREER_READINESS_DISCLAIMER,
            analysis_version="v1.0-deterministic",
        )
        db.add(analysis)
        db.flush()

        # 7. Add gap findings & generate actionable recommendations
        for gap_data in gaps_to_create:
            gap = CareerSkillGapFinding(
                analysis_id=analysis.id,
                institution_id=institution_id,
                student_id=student_id,
                role_id=role_id,
                requirement_id=gap_data.get("requirement_id"),
                competency_name=gap_data["competency_name"],
                importance=gap_data["importance"],
                gap_type=gap_data["gap_type"],
                current_evidence_state=gap_data["current_evidence_state"],
                gap_severity=gap_data["gap_severity"],
                rationale=gap_data["rationale"],
                suggested_action=gap_data["suggested_action"],
                evidence_needed=gap_data["evidence_needed"],
                status="ACTIVE",
            )
            db.add(gap)
            db.flush()

            # Create actionable recommendation for discovered skill gaps
            rec_type = CareerRecommendationType.PRACTICAL_PROJECT.value
            if gap_data["gap_type"] == CareerSkillGapType.MAPPING_GAP.value:
                rec_type = CareerRecommendationType.FACULTY_CONSULTATION.value
            elif "algorithm" in gap_data["competency_name"].lower() or "dsa" in gap_data["competency_name"].lower():
                rec_type = CareerRecommendationType.DSA_PRACTICE.value
            elif "database" in gap_data["competency_name"].lower() or "sql" in gap_data["competency_name"].lower():
                rec_type = CareerRecommendationType.DATABASE_EXERCISE.value
            elif "architecture" in gap_data["competency_name"].lower() or "design" in gap_data["competency_name"].lower():
                rec_type = CareerRecommendationType.SYSTEM_DESIGN.value

            rec = CareerDevelopmentRecommendation(
                analysis_id=analysis.id,
                gap_id=gap.id,
                institution_id=institution_id,
                student_id=student_id,
                role_id=role_id,
                title=f"Address {gap_data['competency_name']} Skill Gap",
                target_competency=gap_data["competency_name"],
                recommendation_type=rec_type,
                priority=gap_data["gap_severity"],
                action_plan=gap_data["suggested_action"],
                expected_evidence=gap_data["evidence_needed"],
                estimated_duration_days=14 if gap_data["gap_severity"] == CareerGapSeverity.HIGH.value else 21,
                status=CareerRecommendationStatus.PROPOSED.value,
            )
            db.add(rec)

        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def compare_roles(
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
        role_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Allows students to compare multiple role profiles side-by-side without forcing a singular path.
        """
        query = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.is_active == True)
        if role_ids:
            query = query.filter(IndustryRoleProfile.id.in_(role_ids))
        roles = query.all()

        comparison = []
        for r in roles:
            # Get latest analysis or run quick evaluation
            analysis = db.query(CareerReadinessAnalysis).filter(
                CareerReadinessAnalysis.student_id == student_id,
                CareerReadinessAnalysis.role_id == r.id,
            ).order_by(CareerReadinessAnalysis.created_at.desc()).first()

            if not analysis:
                analysis = CareerReadinessAnalysisService.analyze_role_readiness(
                    db, student_id, r.id, institution_id
                )

            active_gaps = db.query(CareerSkillGapFinding).filter(
                CareerSkillGapFinding.analysis_id == analysis.id,
                CareerSkillGapFinding.status == "ACTIVE",
            ).count()

            comparison.append({
                "role_id": r.id,
                "role_title": r.role_title,
                "alignment_status": analysis.alignment_status,
                "total_requirements": analysis.total_requirements_count,
                "demonstrated_count": analysis.demonstrated_count,
                "developing_count": analysis.developing_count,
                "gap_count": active_gaps,
                "core_coverage_pct": analysis.core_competency_coverage,
                "practical_coverage_pct": analysis.practical_evidence_coverage,
            })

        return comparison
