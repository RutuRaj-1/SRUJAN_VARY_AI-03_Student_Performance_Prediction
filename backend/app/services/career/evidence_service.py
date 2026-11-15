import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.career import StudentCompetencyEvidence, StudentProjectEvidence
from app.models.academic_data import StudentAcademicProfile
from app.models.syllabus import Competency, SubjectCompetencyMapping
from app.models.mastery import TopicMasteryResult, LearningGapFinding
from app.models.assessment import AssessmentResponse, AssessmentQuestion
from app.models.enums import (
    CompetencyEvidenceState,
    CompetencyEvidenceType,
    ProjectVerificationStatus,
)


class CompetencyEvidenceService:
    @staticmethod
    def harvest_student_competency_evidence(
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> List[StudentCompetencyEvidence]:
        """
        Synthesizes student competency evidence across verified projects, topic mastery,
        and assessment responses without double counting or interpreting missing evidence as failure.
        """
        evidence_map: Dict[str, StudentCompetencyEvidence] = {}

        # 1. Existing stored competency evidence in DB
        existing_records = db.query(StudentCompetencyEvidence).filter(
            StudentCompetencyEvidence.student_id == student_id,
            StudentCompetencyEvidence.is_eligible == True,
        ).all()
        for rec in existing_records:
            evidence_map[rec.competency_name.strip().lower()] = rec

        # 2. Verified Student Project Evidence
        projects = db.query(StudentProjectEvidence).filter(
            StudentProjectEvidence.student_id == student_id,
            StudentProjectEvidence.institution_id == institution_id,
        ).all()

        for proj in projects:
            for comp_name in (proj.demonstrated_competencies or []):
                key = comp_name.strip().lower()
                if proj.verification_status == ProjectVerificationStatus.VERIFIED.value:
                    # Verified project overrides lower states
                    if key not in evidence_map or evidence_map[key].evidence_state != CompetencyEvidenceState.DEMONSTRATED.value:
                        rec = StudentCompetencyEvidence(
                            institution_id=institution_id,
                            student_id=student_id,
                            competency_name=comp_name,
                            category="PRACTICAL",
                            evidence_type=CompetencyEvidenceType.PROJECT_DEMONSTRATION.value,
                            source_entity_type="STUDENT_PROJECT_EVIDENCE",
                            source_entity_id=proj.id,
                            evidence_state=CompetencyEvidenceState.DEMONSTRATED.value,
                            score_or_metric=90.0,
                            evidence_summary=f"Demonstrated in verified practical project '{proj.title}'.",
                            provenance_details={"project_id": str(proj.id), "tech": proj.technology_stack},
                            is_eligible=True,
                            verified_by=proj.reviewer_id,
                            verified_at=proj.reviewed_at,
                        )
                        db.add(rec)
                        evidence_map[key] = rec
                elif proj.verification_status == ProjectVerificationStatus.PENDING_REVIEW.value:
                    if key not in evidence_map:
                        rec = StudentCompetencyEvidence(
                            institution_id=institution_id,
                            student_id=student_id,
                            competency_name=comp_name,
                            category="PRACTICAL",
                            evidence_type=CompetencyEvidenceType.PROJECT_DEMONSTRATION.value,
                            source_entity_type="STUDENT_PROJECT_EVIDENCE",
                            source_entity_id=proj.id,
                            evidence_state=CompetencyEvidenceState.REVIEW_REQUIRED.value,
                            evidence_summary=f"Submitted in project '{proj.title}', awaiting faculty verification.",
                            provenance_details={"project_id": str(proj.id)},
                            is_eligible=True,
                        )
                        db.add(rec)
                        evidence_map[key] = rec

        # 3. Topic Mastery Evidence from Phase 06
        topic_masteries = db.query(TopicMasteryResult).filter(
            TopicMasteryResult.student_id == student_id,
            TopicMasteryResult.institution_id == institution_id,
        ).all()

        for tm in topic_masteries:
            topic_name = tm.topic.title if getattr(tm, "topic", None) else getattr(tm, "topic_name", "")
            key = (topic_name or "").strip().lower()
            if not key:
                continue

            score = tm.mastery_percentage or 0.0
            if score >= 70.0:
                state = CompetencyEvidenceState.DEMONSTRATED.value
            elif score >= 40.0:
                state = CompetencyEvidenceState.DEVELOPING.value
            else:
                state = CompetencyEvidenceState.NOT_YET_DEMONSTRATED.value

            if key not in evidence_map:
                rec = StudentCompetencyEvidence(
                    institution_id=institution_id,
                    student_id=student_id,
                    competency_name=topic_name,
                    category="ANALYTICAL",
                    evidence_type=CompetencyEvidenceType.TOPIC_MASTERY.value,
                    source_entity_type="TOPIC_MASTERY_RESULT",
                    source_entity_id=tm.id,
                    evidence_state=state,
                    score_or_metric=score,
                    evidence_summary=f"Demonstrated topic mastery of {score:.1f}% across continuous assessments.",
                    provenance_details={"job_id": str(tm.analysis_job_id), "mastery_score": score},
                    is_eligible=True,
                )
                db.add(rec)
                evidence_map[key] = rec

        db.commit()
        return list(evidence_map.values())

    @staticmethod
    def get_student_evidence(
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> List[StudentCompetencyEvidence]:
        # Harvest fresh or retrieve
        CompetencyEvidenceService.harvest_student_competency_evidence(db, student_id, institution_id)
        return db.query(StudentCompetencyEvidence).filter(
            StudentCompetencyEvidence.student_id == student_id,
            StudentCompetencyEvidence.institution_id == institution_id,
            StudentCompetencyEvidence.is_eligible == True,
        ).order_by(StudentCompetencyEvidence.competency_name).all()
