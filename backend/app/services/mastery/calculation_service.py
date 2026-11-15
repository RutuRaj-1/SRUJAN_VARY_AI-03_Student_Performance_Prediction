import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.syllabus import SyllabusTopic, SyllabusUnit
from app.models.mastery import MasteryEvidenceRecord, TopicMasteryResult
from app.models.enums import (
    EvidenceEligibilityStatus,
    EvidenceSufficiencyLevel,
    ConfidenceCategory,
    MasteryStatus,
)
from app.core.logging import logger


class TopicMasteryCalculationService:
    """
    Deterministic Topic Mastery Calculation Engine.
    Aggregates eligible evidence per topic and computes:
    - Normalized percentage: P = (sum(marks_obtained) / sum(max_marks)) * 100
    - Sufficiency level: INSUFFICIENT, LIMITED, MODERATE, STRONG
    - Confidence category: LOW, MEDIUM, HIGH
    - Mastery status: MASTERED (>=80%), PROGRESSING (50%-79%), NEEDS_ATTENTION (<50%), INSUFFICIENT_EVIDENCE
    """

    @staticmethod
    def calculate_topic_mastery(
        db: Session,
        institution_id: uuid.UUID,
        analysis_job_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        evidence_records: List[MasteryEvidenceRecord],
        curriculum_version: Optional[str] = "2024.1",
        calculation_version: str = "v1.0-deterministic",
    ) -> List[TopicMasteryResult]:
        # 1. Fetch all approved topics in subject syllabus
        topics = db.execute(
            select(SyllabusTopic)
            .join(SyllabusUnit, SyllabusTopic.unit_id == SyllabusUnit.id)
            .where(SyllabusUnit.subject_id == subject_id)
            .order_by(SyllabusUnit.unit_number.asc(), SyllabusTopic.order_index.asc())
        ).scalars().all()

        results: List[TopicMasteryResult] = []

        # 2. Group eligible evidence by topic_id
        topic_evidence_map: Dict[uuid.UUID, List[MasteryEvidenceRecord]] = {t.id: [] for t in topics}
        for rec in evidence_records:
            if rec.topic_id and rec.topic_id in topic_evidence_map:
                if rec.eligibility_status == EvidenceEligibilityStatus.ELIGIBLE.value:
                    topic_evidence_map[rec.topic_id].append(rec)

        now = datetime.now(timezone.utc)

        # 3. Compute topic mastery for every topic in the syllabus
        for topic in topics:
            records = topic_evidence_map.get(topic.id, [])

            if not records:
                # Topic has NO eligible assessment evidence
                # CRITICAL RULE: Never label missing evidence as poor performance (0%)!
                result = TopicMasteryResult(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=topic.id,
                    curriculum_version=curriculum_version,
                    eligible_question_count=0,
                    eligible_attempt_count=0,
                    marks_obtained=0.0,
                    maximum_marks=0.0,
                    mastery_percentage=None,  # Explicit NULL indicates unassessed
                    evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
                    confidence_category=ConfidenceCategory.LOW.value,
                    mastery_status=MasteryStatus.INSUFFICIENT_EVIDENCE.value,
                    evidence_window_start=None,
                    evidence_window_end=None,
                    calculation_version=calculation_version,
                    calculated_at=now,
                )
                results.append(result)
                continue

            # Compute sums
            total_obtained = sum(r.marks_obtained for r in records)
            total_maximum = sum(r.maximum_marks for r in records)
            unique_questions = len({r.question_id for r in records if r.question_id})
            unique_attempts = len({r.attempt_id for r in records if r.attempt_id})
            unique_assessments = len({r.assessment_id for r in records if r.assessment_id})

            timestamps = [r.evidence_timestamp for r in records if r.evidence_timestamp]
            window_start = min(timestamps) if timestamps else now
            window_end = max(timestamps) if timestamps else now

            # Normalize percentage
            percentage = (total_obtained / total_maximum * 100.0) if total_maximum > 0 else 0.0
            percentage = round(max(0.0, min(100.0, percentage)), 2)

            # Determine Evidence Sufficiency
            # INSUFFICIENT: 0 items or total_max <= 0
            # LIMITED: 1 item or total_max < 5.0
            # MODERATE: >= 2 items across >= 1 assessment, total_max >= 5.0
            # STRONG: >= 3 items across >= 2 independent assessments, total_max >= 15.0
            if unique_questions <= 0 or total_maximum <= 0:
                sufficiency = EvidenceSufficiencyLevel.INSUFFICIENT.value
                confidence = ConfidenceCategory.LOW.value
            elif unique_questions == 1 or total_maximum < 5.0:
                sufficiency = EvidenceSufficiencyLevel.LIMITED.value
                confidence = ConfidenceCategory.LOW.value
            elif unique_questions >= 3 and unique_assessments >= 2 and total_maximum >= 15.0:
                sufficiency = EvidenceSufficiencyLevel.STRONG.value
                confidence = ConfidenceCategory.HIGH.value
            else:
                sufficiency = EvidenceSufficiencyLevel.MODERATE.value
                confidence = ConfidenceCategory.MEDIUM.value

            # Determine Mastery Status
            if sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value:
                status = MasteryStatus.INSUFFICIENT_EVIDENCE.value
                final_percentage = None
            elif percentage >= 80.0 and sufficiency in [EvidenceSufficiencyLevel.MODERATE.value, EvidenceSufficiencyLevel.STRONG.value]:
                status = MasteryStatus.MASTERED.value
                final_percentage = percentage
            elif percentage >= 50.0:
                status = MasteryStatus.PROGRESSING.value
                final_percentage = percentage
            else:
                status = MasteryStatus.NEEDS_ATTENTION.value
                final_percentage = percentage

            result = TopicMasteryResult(
                id=uuid.uuid4(),
                institution_id=institution_id,
                analysis_job_id=analysis_job_id,
                student_id=student_id,
                subject_id=subject_id,
                topic_id=topic.id,
                curriculum_version=curriculum_version,
                eligible_question_count=unique_questions,
                eligible_attempt_count=unique_attempts,
                marks_obtained=round(total_obtained, 2),
                maximum_marks=round(total_maximum, 2),
                mastery_percentage=final_percentage,
                evidence_sufficiency=sufficiency,
                confidence_category=confidence,
                mastery_status=status,
                evidence_window_start=window_start,
                evidence_window_end=window_end,
                calculation_version=calculation_version,
                calculated_at=now,
            )
            results.append(result)

        return results
