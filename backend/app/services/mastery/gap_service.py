import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.syllabus import SyllabusTopic, LearningOutcome
from app.models.mastery import TopicMasteryResult, LearningOutcomeAttainmentResult, LearningGapFinding
from app.models.enums import (
    LearningGapType,
    LearningGapSeverity,
    MasteryStatus,
    AttainmentStatus,
    EvidenceSufficiencyLevel,
)
from app.core.logging import logger


class LearningGapAnalysisService:
    """
    Deterministic Learning Gap Discovery Engine.
    Distinguishes genuine academic difficulty from missing or insufficient evidence.
    Generates findings with explicit severity and faculty-actionable recommendations.
    """

    @staticmethod
    def identify_learning_gaps(
        db: Session,
        institution_id: uuid.UUID,
        analysis_job_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        topic_results: List[TopicMasteryResult],
        outcome_results: List[LearningOutcomeAttainmentResult],
    ) -> List[LearningGapFinding]:
        findings: List[LearningGapFinding] = []
        now = datetime.now(timezone.utc)

        # 1. Inspect Topic Mastery Results
        for tr in topic_results:
            topic = tr.topic

            # Finding Type 1: LOW_DEMONSTRATED_PERFORMANCE
            if tr.mastery_status == MasteryStatus.NEEDS_ATTENTION.value and tr.mastery_percentage is not None:
                severity = (
                    LearningGapSeverity.CRITICAL.value
                    if tr.mastery_percentage < 35.0
                    else LearningGapSeverity.HIGH.value
                )
                finding = LearningGapFinding(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=tr.topic_id,
                    learning_outcome_id=None,
                    finding_type=LearningGapType.LOW_DEMONSTRATED_PERFORMANCE.value,
                    severity=severity,
                    evidence_summary=(
                        f"Demonstrated topic mastery is {tr.mastery_percentage}% "
                        f"({tr.marks_obtained}/{tr.maximum_marks} marks across {tr.eligible_question_count} questions). "
                        f"Evidence sufficiency is {tr.evidence_sufficiency}."
                    ),
                    supporting_evidence_refs={
                        "topic_id": str(tr.topic_id),
                        "mastery_percentage": tr.mastery_percentage,
                        "eligible_questions": tr.eligible_question_count,
                        "sufficiency": tr.evidence_sufficiency,
                    },
                    recommended_review_action=(
                        f"Review foundational concept explanations for '{topic.topic_name if topic else 'this topic'}'. "
                        f"Assign targeted diagnostic practice exercises."
                    ),
                    status="OPEN",
                    created_at=now,
                    updated_at=now,
                )
                findings.append(finding)

            # Finding Type 2: INSUFFICIENT_EVIDENCE
            elif tr.evidence_sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value:
                finding = LearningGapFinding(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=tr.topic_id,
                    learning_outcome_id=None,
                    finding_type=LearningGapType.INSUFFICIENT_EVIDENCE.value,
                    severity=LearningGapSeverity.INFO.value,
                    evidence_summary=(
                        f"Zero eligible assessment items recorded for topic "
                        f"'{topic.topic_name if topic else str(tr.topic_id)}'. Performance is currently unknown."
                    ),
                    supporting_evidence_refs={"topic_id": str(tr.topic_id), "eligible_questions": 0},
                    recommended_review_action="Schedule a formative assessment or diagnostic quiz to evaluate understanding.",
                    status="OPEN",
                    created_at=now,
                    updated_at=now,
                )
                findings.append(finding)

        # 2. Inspect Learning Outcome Attainment Results
        for lo_res in outcome_results:
            lo = lo_res.learning_outcome
            if lo_res.attainment_status == AttainmentStatus.NOT_ATTAINED.value and lo_res.attainment_percentage is not None:
                finding = LearningGapFinding(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=None,
                    learning_outcome_id=lo_res.learning_outcome_id,
                    finding_type=LearningGapType.LOW_DEMONSTRATED_PERFORMANCE.value,
                    severity=LearningGapSeverity.HIGH.value,
                    evidence_summary=(
                        f"Course learning outcome '{lo.outcome_code if lo else 'CLO'}' attainment is {lo_res.attainment_percentage}%. "
                        f"Description: '{lo.description if lo else ''}'."
                    ),
                    supporting_evidence_refs={
                        "learning_outcome_id": str(lo_res.learning_outcome_id),
                        "attainment_percentage": lo_res.attainment_percentage,
                        "bloom_level": lo.bloom_level if lo else None,
                    },
                    recommended_review_action=f"Reinforce cognitive learning objectives for {lo.outcome_code if lo else 'outcome'}.",
                    status="OPEN",
                    created_at=now,
                    updated_at=now,
                )
                findings.append(finding)

        return findings
