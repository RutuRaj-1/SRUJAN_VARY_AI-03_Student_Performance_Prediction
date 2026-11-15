import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.interventions import (
    AcademicInterventionRecommendation,
    InterventionTemplate,
    DEFAULT_INTERVENTION_DISCLAIMER,
)
from app.models.mastery import TopicMasteryResult, LearningGapFinding
from app.models.risk import AcademicRiskPrediction
from app.models.academic_data import StudentAcademicProfile
from app.models.syllabus import AcademicSubject, SyllabusTopic
from app.models.enums import (
    InterventionType,
    InterventionPriority,
    InterventionRecommendationStatus,
    EvidenceSufficiencyLevel,
    RiskClassification,
)
from app.services.interventions.template_service import intervention_template_service
from app.core.logging import logger


class InterventionRecommendationService:
    @staticmethod
    def generate_recommendations_for_student(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        topic_id: Optional[uuid.UUID] = None,
        template_id: Optional[uuid.UUID] = None,
    ) -> List[AcademicInterventionRecommendation]:
        """
        Generates evidence-grounded academic intervention recommendations for a student in a subject.
        Combines Phase 06 Learning Gaps, Topic Mastery, and Phase 07 Risk Predictions.
        """
        # Ensure templates exist
        intervention_template_service.seed_default_templates_if_empty(db, institution_id)

        # 1. Fetch Phase 06 Topic Gaps
        gaps_query = (
            db.query(LearningGapFinding)
            .filter(
                LearningGapFinding.institution_id == institution_id,
                LearningGapFinding.student_id == student_id,
                LearningGapFinding.subject_id == subject_id,
                LearningGapFinding.status != "RESOLVED",
            )
        )
        if topic_id:
            gaps_query = gaps_query.filter(LearningGapFinding.topic_id == topic_id)
        open_gaps = gaps_query.all()

        # 2. Fetch Phase 06 Topic Mastery Results
        mastery_query = (
            db.query(TopicMasteryResult)
            .filter(
                TopicMasteryResult.institution_id == institution_id,
                TopicMasteryResult.student_id == student_id,
                TopicMasteryResult.subject_id == subject_id,
            )
        )
        if topic_id:
            mastery_query = mastery_query.filter(TopicMasteryResult.topic_id == topic_id)
        mastery_results = mastery_query.all()

        # 3. Fetch Phase 07 Risk Prediction
        risk_prediction = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.institution_id == institution_id,
                AcademicRiskPrediction.student_id == student_id,
                AcademicRiskPrediction.subject_id == subject_id,
            )
            .order_by(AcademicRiskPrediction.created_at.desc())
            .first()
        )

        # Check existing active recommendations to prevent duplicate flooding
        existing_recs = (
            db.query(AcademicInterventionRecommendation)
            .filter(
                AcademicInterventionRecommendation.institution_id == institution_id,
                AcademicInterventionRecommendation.student_id == student_id,
                AcademicInterventionRecommendation.subject_id == subject_id,
                AcademicInterventionRecommendation.status == InterventionRecommendationStatus.ACTIVE.value,
            )
            .all()
        )
        existing_topic_ids = {r.topic_id for r in existing_recs if r.topic_id}

        created_recommendations: List[AcademicInterventionRecommendation] = []

        # ---------------------------------------------------------------------
        # CASE A: Insufficient Evidence Handling
        # ---------------------------------------------------------------------
        # If risk prediction reports INSUFFICIENT_EVIDENCE or mastery results are mostly unassessed
        has_insufficient_risk = (
            risk_prediction and risk_prediction.risk_classification == RiskClassification.INSUFFICIENT_EVIDENCE.value
        )
        insufficient_topics = [
            m for m in mastery_results if m.evidence_sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value
        ]

        if (has_insufficient_risk or insufficient_topics) and not open_gaps:
            target_topic = insufficient_topics[0] if insufficient_topics else None
            target_t_id = target_topic.topic_id if target_topic else topic_id

            if not target_t_id or target_t_id not in existing_topic_ids:
                diag_rec = AcademicInterventionRecommendation(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=target_t_id,
                    risk_prediction_id=risk_prediction.id if risk_prediction else None,
                    recommendation_type=InterventionType.FORMATIVE_ASSESSMENT.value,
                    priority=InterventionPriority.LOW.value,
                    rationale=(
                        "Assessment evidence is currently insufficient to reliably assess topic mastery or academic risk. "
                        "A low-stakes formative evaluation is recommended to establish an empirical learning baseline."
                    ),
                    source_evidence_summary={
                        "risk_classification": "INSUFFICIENT_EVIDENCE",
                        "reason": "Fewer than 2 continuous assessment records on file",
                        "policy": "Formative evidence gathering prior to remedial intervention",
                    },
                    evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
                    proposed_action_title="Complete Low-Stakes Formative Diagnostic Assessment",
                    proposed_action_description=(
                        "Attempt an un-graded 10-question diagnostic exercise covering foundational syllabus concepts."
                    ),
                    suggested_duration_days=5,
                    status=InterventionRecommendationStatus.ACTIVE.value,
                    scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
                )
                db.add(diag_rec)
                created_recommendations.append(diag_rec)
                if target_t_id:
                    existing_topic_ids.add(target_t_id)

        # ---------------------------------------------------------------------
        # CASE B: Persistent Verified Low Performance (Phase 06 Gaps)
        # ---------------------------------------------------------------------
        for gap in open_gaps:
            if gap.topic_id and gap.topic_id in existing_topic_ids:
                continue

            topic = db.query(SyllabusTopic).filter(SyllabusTopic.id == gap.topic_id).first() if gap.topic_id else None
            topic_name = topic.topic_name if topic else "Syllabus Topic"

            priority = (
                InterventionPriority.CRITICAL.value
                if gap.severity == "CRITICAL"
                else InterventionPriority.HIGH.value
                if gap.severity == "HIGH"
                else InterventionPriority.MEDIUM.value
            )

            rec = AcademicInterventionRecommendation(
                id=uuid.uuid4(),
                institution_id=institution_id,
                student_id=student_id,
                subject_id=subject_id,
                topic_id=gap.topic_id,
                learning_gap_id=gap.id,
                risk_prediction_id=risk_prediction.id if risk_prediction else None,
                template_id=template_id,
                recommendation_type=InterventionType.TARGETED_REVISION.value,
                priority=priority,
                rationale=(
                    f"Verified learning gap detected on topic '{topic_name}' ({gap.evidence_summary}). "
                    f"Targeted conceptual review and guided practice is recommended to reinforce comprehension."
                ),
                source_evidence_summary={
                    "gap_id": str(gap.id),
                    "finding_type": gap.finding_type,
                    "severity": gap.severity,
                    "evidence_summary": gap.evidence_summary,
                    "supporting_evidence_refs": gap.supporting_evidence_refs or {},
                },
                evidence_sufficiency=EvidenceSufficiencyLevel.MODERATE.value,
                proposed_action_title=f"Targeted Conceptual Revision: {topic_name}",
                proposed_action_description=(
                    f"Review core lecture notes on '{topic_name}', examine worked example solutions, "
                    f"and complete 3 formative practice problems."
                ),
                suggested_duration_days=7,
                status=InterventionRecommendationStatus.ACTIVE.value,
                scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
            )
            db.add(rec)
            created_recommendations.append(rec)
            if gap.topic_id:
                existing_topic_ids.add(gap.topic_id)

        # ---------------------------------------------------------------------
        # CASE C: High or Critical Academic Risk (Phase 07)
        # ---------------------------------------------------------------------
        if risk_prediction and risk_prediction.risk_classification == RiskClassification.HIGH.value:
            # Check if there is already a course-level consultation recommendation
            has_advisory = any(r.topic_id is None for r in existing_recs)
            if not has_advisory:
                advisory_rec = AcademicInterventionRecommendation(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=None,
                    risk_prediction_id=risk_prediction.id,
                    recommendation_type=InterventionType.FACULTY_CONSULTATION.value,
                    priority=InterventionPriority.HIGH.value,
                    rationale=(
                        f"Early warning predictive screening indicates elevated deficit probability "
                        f"({(risk_prediction.risk_score * 100):.0f}% risk score). "
                        f"A 1-on-1 faculty advisory consultation is recommended to co-design an individual recovery roadmap."
                    ),
                    source_evidence_summary={
                        "risk_prediction_id": str(risk_prediction.id),
                        "risk_classification": risk_prediction.risk_classification,
                        "risk_score": risk_prediction.risk_score,
                        "explanations_count": len(risk_prediction.explanations) if hasattr(risk_prediction, "explanations") else 0,
                    },
                    evidence_sufficiency=risk_prediction.evidence_sufficiency,
                    proposed_action_title="Faculty Advising & Recovery Planning Session",
                    proposed_action_description=(
                        "Schedule an office-hours meeting with course instructor to review continuous assessment feedback "
                        "and establish weekly milestones."
                    ),
                    suggested_duration_days=7,
                    status=InterventionRecommendationStatus.ACTIVE.value,
                    scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
                )
                db.add(advisory_rec)
                created_recommendations.append(advisory_rec)

        db.commit()
        for r in created_recommendations:
            db.refresh(r)

        logger.info(
            f"Generated {len(created_recommendations)} intervention recommendations for student {student_id} in subject {subject_id}"
        )
        return created_recommendations

    @staticmethod
    def get_recommendations(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[AcademicInterventionRecommendation]:
        query = db.query(AcademicInterventionRecommendation).filter(
            AcademicInterventionRecommendation.institution_id == institution_id
        )
        if subject_id:
            query = query.filter(AcademicInterventionRecommendation.subject_id == subject_id)
        if student_id:
            query = query.filter(AcademicInterventionRecommendation.student_id == student_id)
        if status:
            query = query.filter(AcademicInterventionRecommendation.status == status)

        return query.order_by(AcademicInterventionRecommendation.created_at.desc()).all()


intervention_recommendation_service = InterventionRecommendationService()
