import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.syllabus import LearningOutcome
from app.models.mastery import MasteryEvidenceRecord, LearningOutcomeAttainmentResult
from app.models.enums import (
    EvidenceEligibilityStatus,
    EvidenceSufficiencyLevel,
    ConfidenceCategory,
    AttainmentStatus,
)
from app.core.logging import logger


class LearningOutcomeAttainmentService:
    """
    Deterministic Learning Outcome (CLO) Attainment Engine.
    Aggregates eligible evidence mapped to each learning outcome.
    Preserves distinction between:
    - Outcome Coverage (whether assessed)
    - Outcome Attainment (percentage score achieved on assessed items)
    - Insufficient Evidence (unassessed outcomes never receive 0%)
    """

    @staticmethod
    def calculate_outcome_attainment(
        db: Session,
        institution_id: uuid.UUID,
        analysis_job_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        evidence_records: List[MasteryEvidenceRecord],
        calculation_version: str = "v1.0-deterministic",
    ) -> List[LearningOutcomeAttainmentResult]:
        # 1. Fetch all syllabus learning outcomes for this subject
        outcomes = db.execute(
            select(LearningOutcome)
            .where(LearningOutcome.subject_id == subject_id)
            .order_by(LearningOutcome.outcome_code.asc())
        ).scalars().all()

        results: List[LearningOutcomeAttainmentResult] = []

        # 2. Group eligible evidence by learning_outcome_id
        outcome_evidence_map: Dict[uuid.UUID, List[MasteryEvidenceRecord]] = {lo.id: [] for lo in outcomes}
        for rec in evidence_records:
            if rec.learning_outcome_id and rec.learning_outcome_id in outcome_evidence_map:
                if rec.eligibility_status == EvidenceEligibilityStatus.ELIGIBLE.value:
                    outcome_evidence_map[rec.learning_outcome_id].append(rec)

        now = datetime.now(timezone.utc)

        # 3. Calculate attainment per outcome
        for lo in outcomes:
            records = outcome_evidence_map.get(lo.id, [])

            if not records:
                # Outcome was never assessed for this candidate
                # RULE: Never default unassessed outcome to 0%!
                result = LearningOutcomeAttainmentResult(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    learning_outcome_id=lo.id,
                    eligible_question_count=0,
                    mapped_marks=0.0,
                    marks_obtained=0.0,
                    attainment_percentage=None,
                    evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
                    confidence_category=ConfidenceCategory.LOW.value,
                    attainment_status=AttainmentStatus.INSUFFICIENT_EVIDENCE.value,
                    calculation_version=calculation_version,
                    calculated_at=now,
                )
                results.append(result)
                continue

            total_obtained = sum(r.marks_obtained for r in records)
            total_mapped_marks = sum(r.maximum_marks for r in records)
            unique_questions = len({r.question_id for r in records if r.question_id})
            unique_assessments = len({r.assessment_id for r in records if r.assessment_id})

            percentage = (total_obtained / total_mapped_marks * 100.0) if total_mapped_marks > 0 else 0.0
            percentage = round(max(0.0, min(100.0, percentage)), 2)

            # Sufficiency determination
            if unique_questions <= 0 or total_mapped_marks <= 0:
                sufficiency = EvidenceSufficiencyLevel.INSUFFICIENT.value
                confidence = ConfidenceCategory.LOW.value
            elif unique_questions == 1 or total_mapped_marks < 5.0:
                sufficiency = EvidenceSufficiencyLevel.LIMITED.value
                confidence = ConfidenceCategory.LOW.value
            elif unique_questions >= 3 and unique_assessments >= 2 and total_mapped_marks >= 10.0:
                sufficiency = EvidenceSufficiencyLevel.STRONG.value
                confidence = ConfidenceCategory.HIGH.value
            else:
                sufficiency = EvidenceSufficiencyLevel.MODERATE.value
                confidence = ConfidenceCategory.MEDIUM.value

            # Attainment Status
            if sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value:
                status = AttainmentStatus.INSUFFICIENT_EVIDENCE.value
                final_percentage = None
            elif percentage >= 75.0:
                status = AttainmentStatus.ATTAINED.value
                final_percentage = percentage
            elif percentage >= 45.0:
                status = AttainmentStatus.PARTIALLY_ATTAINED.value
                final_percentage = percentage
            else:
                status = AttainmentStatus.NOT_ATTAINED.value
                final_percentage = percentage

            result = LearningOutcomeAttainmentResult(
                id=uuid.uuid4(),
                institution_id=institution_id,
                analysis_job_id=analysis_job_id,
                student_id=student_id,
                subject_id=subject_id,
                learning_outcome_id=lo.id,
                eligible_question_count=unique_questions,
                mapped_marks=round(total_mapped_marks, 2),
                marks_obtained=round(total_obtained, 2),
                attainment_percentage=final_percentage,
                evidence_sufficiency=sufficiency,
                confidence_category=confidence,
                attainment_status=status,
                calculation_version=calculation_version,
                calculated_at=now,
            )
            results.append(result)

        return results
