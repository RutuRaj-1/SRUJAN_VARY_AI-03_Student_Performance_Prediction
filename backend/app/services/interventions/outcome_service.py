import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.interventions import (
    AcademicInterventionPlan,
    InterventionOutcomeObservation,
    DEFAULT_INTERVENTION_DISCLAIMER,
)
from app.models.mastery import TopicMasteryResult
from app.models.academic_data import AcademicAssessment
from app.schemas.interventions import InterventionOutcomeCreate
from app.core.logging import logger


class InterventionOutcomeService:
    @staticmethod
    def record_outcome_observation(
        db: Session,
        institution_id: uuid.UUID,
        plan_id: uuid.UUID,
        payload: InterventionOutcomeCreate,
    ) -> InterventionOutcomeObservation:
        """
        Records post-intervention observational evidence for an intervention plan.
        Strictly frames results as observational follow-up without unproven causal claims.
        """
        plan = (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.id == plan_id,
                AcademicInterventionPlan.institution_id == institution_id,
            )
            .first()
        )
        if not plan:
            raise HTTPException(status_code=404, detail="Intervention plan not found")

        # Automatically retrieve baseline mastery percentage if topic_id is present and not provided
        baseline_pct = payload.baseline_mastery_percentage
        if baseline_pct is None and plan.topic_id:
            mastery = (
                db.query(TopicMasteryResult)
                .filter(
                    TopicMasteryResult.student_id == plan.student_id,
                    TopicMasteryResult.subject_id == plan.subject_id,
                    TopicMasteryResult.topic_id == plan.topic_id,
                )
                .first()
            )
            if mastery and mastery.mastery_percentage is not None:
                baseline_pct = mastery.mastery_percentage

        # Compute follow-up mastery percentage if marks provided
        followup_pct = payload.followup_mastery_percentage
        if followup_pct is None and payload.followup_score_obtained is not None and payload.followup_maximum_marks:
            if payload.followup_maximum_marks > 0:
                followup_pct = round((payload.followup_score_obtained / payload.followup_maximum_marks) * 100.0, 2)

        observation = InterventionOutcomeObservation(
            id=uuid.uuid4(),
            institution_id=institution_id,
            plan_id=plan.id,
            student_id=plan.student_id,
            subject_id=plan.subject_id,
            topic_id=plan.topic_id,
            learning_outcome_id=plan.learning_outcome_id,
            baseline_mastery_percentage=baseline_pct,
            followup_assessment_id=payload.followup_assessment_id,
            followup_score_obtained=payload.followup_score_obtained,
            followup_maximum_marks=payload.followup_maximum_marks,
            followup_mastery_percentage=followup_pct,
            observation_notes=payload.observation_notes,
            scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)
        logger.info(f"Recorded outcome observation {observation.id} for plan {plan.id}")
        return observation

    @staticmethod
    def get_outcome_observations_for_plan(
        db: Session,
        institution_id: uuid.UUID,
        plan_id: uuid.UUID,
    ) -> List[InterventionOutcomeObservation]:
        return (
            db.query(InterventionOutcomeObservation)
            .filter(
                InterventionOutcomeObservation.plan_id == plan_id,
                InterventionOutcomeObservation.institution_id == institution_id,
            )
            .order_by(InterventionOutcomeObservation.observed_at.desc())
            .all()
        )


intervention_outcome_service = InterventionOutcomeService()
