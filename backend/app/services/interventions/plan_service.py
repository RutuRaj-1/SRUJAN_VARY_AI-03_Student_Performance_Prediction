import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.interventions import (
    AcademicInterventionPlan,
    AcademicInterventionAction,
    InterventionProgressEvent,
    AcademicInterventionRecommendation,
    InterventionTemplate,
    DEFAULT_INTERVENTION_DISCLAIMER,
)
from app.models.enums import (
    InterventionPlanStatus,
    InterventionActionStatus,
    InterventionEventType,
    InterventionRecommendationStatus,
)
from app.schemas.interventions import (
    InterventionPlanCreate,
    InterventionPlanUpdate,
    InterventionActionCreate,
    InterventionActionStatusUpdate,
)
from app.core.logging import logger


class InterventionPlanService:
    @staticmethod
    def create_plan(
        db: Session,
        institution_id: uuid.UUID,
        payload: InterventionPlanCreate,
        creator_id: Optional[uuid.UUID] = None,
    ) -> AcademicInterventionPlan:
        """
        Creates a new structured Academic Intervention Plan in DRAFT or PENDING_REVIEW status.
        """
        plan = AcademicInterventionPlan(
            id=uuid.uuid4(),
            institution_id=institution_id,
            student_id=payload.student_id,
            subject_id=payload.subject_id,
            topic_id=payload.topic_id,
            learning_outcome_id=payload.learning_outcome_id,
            recommendation_id=payload.recommendation_id,
            plan_title=payload.plan_title,
            learning_objective=payload.learning_objective,
            plan_status=InterventionPlanStatus.PENDING_REVIEW.value,
            assigned_faculty_id=payload.assigned_faculty_id or creator_id,
            target_completion_date=payload.target_completion_date,
            expected_outcome_evidence=payload.expected_outcome_evidence,
            scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
        )
        db.add(plan)
        db.flush()

        # Add initial actions if provided
        action_order = 1
        if payload.initial_actions:
            for act in payload.initial_actions:
                action_entity = AcademicInterventionAction(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    plan_id=plan.id,
                    action_order=action_order,
                    action_title=act.action_title,
                    action_type=act.action_type.value,
                    instructions=act.instructions,
                    resource_references=act.resource_references,
                    estimated_effort_hours=act.estimated_effort_hours,
                    due_date=act.due_date or payload.target_completion_date,
                    action_status=InterventionActionStatus.PROPOSED.value,
                )
                db.add(action_entity)
                action_order += 1
        else:
            # Create a default core revision action
            default_act = AcademicInterventionAction(
                id=uuid.uuid4(),
                institution_id=institution_id,
                plan_id=plan.id,
                action_order=1,
                action_title=f"Complete Core Revision & Practice Tasks for {plan.plan_title}",
                action_type="TARGETED_REVISION",
                instructions="Review lecture notes, resolve diagnostic misconceptions, and submit self-assessment solutions.",
                resource_references=[],
                estimated_effort_hours=2.0,
                due_date=payload.target_completion_date,
                action_status=InterventionActionStatus.PROPOSED.value,
            )
            db.add(default_act)

        # Update recommendation status to ADOPTED_IN_PLAN if linked
        if payload.recommendation_id:
            rec = (
                db.query(AcademicInterventionRecommendation)
                .filter(AcademicInterventionRecommendation.id == payload.recommendation_id)
                .first()
            )
            if rec:
                rec.status = InterventionRecommendationStatus.ADOPTED_IN_PLAN.value

        # Log creation progress event
        event = InterventionProgressEvent(
            id=uuid.uuid4(),
            institution_id=institution_id,
            plan_id=plan.id,
            actor_profile_id=creator_id,
            event_type=InterventionEventType.PLAN_CREATED.value,
            previous_status=None,
            new_status=InterventionPlanStatus.PENDING_REVIEW.value,
            event_notes="Intervention plan authored and queued for faculty review.",
        )
        db.add(event)

        db.commit()
        db.refresh(plan)
        logger.info(f"Created academic intervention plan '{plan.plan_title}' ({plan.id}) for student {plan.student_id}")
        return plan

    @staticmethod
    def review_plan(
        db: Session,
        institution_id: uuid.UUID,
        plan_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        decision: str,  # "APPROVE" or "REJECT"
        review_notes: Optional[str] = None,
        assigned_faculty_id: Optional[uuid.UUID] = None,
    ) -> AcademicInterventionPlan:
        """
        Faculty review checkpoint. Approves or rejects an intervention plan.
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

        prev_status = plan.plan_status
        now = datetime.now(timezone.utc)

        if decision.upper() == "APPROVE":
            plan.plan_status = InterventionPlanStatus.APPROVED.value
            plan.reviewed_by_faculty_id = reviewer_id
            plan.reviewed_at = now
            plan.faculty_review_notes = review_notes
            if assigned_faculty_id:
                plan.assigned_faculty_id = assigned_faculty_id

            event_type = InterventionEventType.PLAN_APPROVED.value
            note = f"Plan approved by faculty: {review_notes or 'Standard pedagogical intervention authorized.'}"

        elif decision.upper() == "REJECT":
            plan.plan_status = InterventionPlanStatus.REJECTED.value
            plan.reviewed_by_faculty_id = reviewer_id
            plan.reviewed_at = now
            plan.faculty_review_notes = review_notes

            event_type = InterventionEventType.PLAN_REJECTED.value
            note = f"Plan rejected during faculty review: {review_notes or 'Intervention not required at this time.'}"

        else:
            raise HTTPException(status_code=400, detail="Invalid review decision. Must be APPROVE or REJECT.")

        event = InterventionProgressEvent(
            id=uuid.uuid4(),
            institution_id=institution_id,
            plan_id=plan.id,
            actor_profile_id=reviewer_id,
            event_type=event_type,
            previous_status=prev_status,
            new_status=plan.plan_status,
            event_notes=note,
        )
        db.add(event)
        db.commit()
        db.refresh(plan)
        logger.info(f"Intervention plan {plan.id} reviewed with decision {decision}")
        return plan

    @staticmethod
    def assign_plan(
        db: Session,
        institution_id: uuid.UUID,
        plan_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> AcademicInterventionPlan:
        """
        Promotes an APPROVED plan to ACTIVE and marks all actions as ASSIGNED.
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

        if plan.plan_status not in (InterventionPlanStatus.APPROVED.value, InterventionPlanStatus.DRAFT.value):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot assign plan with status {plan.plan_status}. Must be APPROVED.",
            )

        prev_status = plan.plan_status
        plan.plan_status = InterventionPlanStatus.ACTIVE.value
        plan.start_date = datetime.now(timezone.utc)

        # Promote all actions to ASSIGNED
        for act in plan.actions:
            if act.action_status == InterventionActionStatus.PROPOSED.value:
                act.action_status = InterventionActionStatus.ASSIGNED.value

        event = InterventionProgressEvent(
            id=uuid.uuid4(),
            institution_id=institution_id,
            plan_id=plan.id,
            actor_profile_id=actor_id,
            event_type=InterventionEventType.PLAN_ASSIGNED.value,
            previous_status=prev_status,
            new_status=InterventionPlanStatus.ACTIVE.value,
            event_notes="Plan activated and dispatched to student dashboard.",
        )
        db.add(event)
        db.commit()
        db.refresh(plan)
        logger.info(f"Assigned and activated intervention plan {plan.id}")
        return plan

    @staticmethod
    def update_action_status(
        db: Session,
        institution_id: uuid.UUID,
        action_id: uuid.UUID,
        payload: InterventionActionStatusUpdate,
        actor_id: uuid.UUID,
        is_faculty: bool = False,
    ) -> AcademicInterventionAction:
        """
        Executes verified lifecycle state transitions for an individual action.
        """
        action = (
            db.query(AcademicInterventionAction)
            .filter(
                AcademicInterventionAction.id == action_id,
                AcademicInterventionAction.institution_id == institution_id,
            )
            .first()
        )
        if not action:
            raise HTTPException(status_code=404, detail="Intervention action not found")

        plan = action.plan
        prev_status = action.action_status
        new_status = payload.new_status.value
        now = datetime.now(timezone.utc)

        # State transition validation
        if new_status == InterventionActionStatus.IN_PROGRESS.value:
            if prev_status not in (InterventionActionStatus.ASSIGNED.value, InterventionActionStatus.PROPOSED.value):
                raise HTTPException(status_code=400, detail=f"Cannot start action from status {prev_status}")
            action.action_status = new_status
            event_type = InterventionEventType.ACTION_STARTED.value
            notes = "Student marked action as in-progress."

        elif new_status == InterventionActionStatus.SUBMITTED.value:
            action.action_status = new_status
            action.student_completion_notes = payload.student_completion_notes
            action.student_submission_url = payload.student_submission_url
            action.submitted_at = now
            event_type = InterventionEventType.ACTION_SUBMITTED.value
            notes = f"Student submitted action evidence: {payload.student_completion_notes or 'Submission complete.'}"

        elif new_status == InterventionActionStatus.VERIFIED.value:
            if not is_faculty:
                raise HTTPException(status_code=403, detail="Only faculty can verify action completion.")
            action.action_status = new_status
            action.faculty_feedback = payload.faculty_feedback
            action.verified_by_faculty_id = actor_id
            action.verified_at = now
            event_type = InterventionEventType.ACTION_VERIFIED.value
            notes = f"Faculty verified action completion: {payload.faculty_feedback or 'Accepted without remarks.'}"

        elif new_status == InterventionActionStatus.DECLINED.value:
            action.action_status = new_status
            event_type = InterventionEventType.ACTION_DECLINED.value
            notes = f"Action declined by student: {payload.student_completion_notes or 'No reason provided.'}"

        elif new_status == InterventionActionStatus.CANCELLED.value:
            action.action_status = new_status
            event_type = "ACTION_CANCELLED"
            notes = "Action cancelled by faculty."

        else:
            action.action_status = new_status
            event_type = f"ACTION_{new_status}"
            notes = f"Action status transitioned to {new_status}"

        # Log action progress event
        event = InterventionProgressEvent(
            id=uuid.uuid4(),
            institution_id=institution_id,
            plan_id=plan.id,
            action_id=action.id,
            actor_profile_id=actor_id,
            event_type=event_type,
            previous_status=prev_status,
            new_status=new_status,
            event_notes=notes,
        )
        db.add(event)

        # Check if all actions in plan are now verified -> Auto-complete plan
        all_actions = (
            db.query(AcademicInterventionAction)
            .filter(AcademicInterventionAction.plan_id == plan.id)
            .all()
        )
        all_completed = all(
            a.action_status in (InterventionActionStatus.VERIFIED.value, InterventionActionStatus.DECLINED.value)
            for a in all_actions
        )
        if all_completed and plan.plan_status == InterventionPlanStatus.ACTIVE.value:
            plan.plan_status = InterventionPlanStatus.COMPLETED.value
            plan.actual_completion_date = now
            comp_event = InterventionProgressEvent(
                id=uuid.uuid4(),
                institution_id=institution_id,
                plan_id=plan.id,
                actor_profile_id=actor_id,
                event_type=InterventionEventType.PLAN_COMPLETED.value,
                previous_status=InterventionPlanStatus.ACTIVE.value,
                new_status=InterventionPlanStatus.COMPLETED.value,
                event_notes="All assigned actions verified. Intervention plan marked as completed.",
            )
            db.add(comp_event)

        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def get_plan_by_id(
        db: Session,
        plan_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> Optional[AcademicInterventionPlan]:
        return (
            db.query(AcademicInterventionPlan)
            .filter(
                AcademicInterventionPlan.id == plan_id,
                AcademicInterventionPlan.institution_id == institution_id,
            )
            .first()
        )

    @staticmethod
    def list_plans(
        db: Session,
        institution_id: uuid.UUID,
        student_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[AcademicInterventionPlan]:
        query = db.query(AcademicInterventionPlan).filter(
            AcademicInterventionPlan.institution_id == institution_id
        )
        if student_id:
            query = query.filter(AcademicInterventionPlan.student_id == student_id)
        if subject_id:
            query = query.filter(AcademicInterventionPlan.subject_id == subject_id)
        if status:
            query = query.filter(AcademicInterventionPlan.plan_status == status)

        return query.order_by(AcademicInterventionPlan.created_at.desc()).all()


intervention_plan_service = InterventionPlanService()
