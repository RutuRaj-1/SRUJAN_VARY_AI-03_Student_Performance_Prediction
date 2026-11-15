import uuid
from typing import List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, require_roles, CurrentUser
from app.models.enums import UserRole, InterventionPlanStatus, InterventionActionStatus
from app.schemas.interventions import (
    InterventionTemplateCreate,
    InterventionTemplateResponse,
    InterventionRecommendationGenerateRequest,
    InterventionRecommendationResponse,
    InterventionPlanCreate,
    InterventionPlanReviewRequest,
    AcademicInterventionPlanResponse,
    InterventionActionStatusUpdate,
    InterventionActionResponse,
    InterventionOutcomeCreate,
    InterventionOutcomeResponse,
    InterventionFacultyDashboardResponse,
    InterventionStudentWorkspaceResponse,
)
from app.services.interventions import (
    intervention_template_service,
    intervention_recommendation_service,
    intervention_plan_service,
    intervention_outcome_service,
)
from app.models.academic_data import StudentAcademicProfile
from app.models.syllabus import AcademicSubject
from app.models.interventions import (
    AcademicInterventionPlan,
    AcademicInterventionAction,
    AcademicInterventionRecommendation,
    DEFAULT_INTERVENTION_DISCLAIMER,
)

router = APIRouter()


def _parse_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


def _assert_not_placement_officer(current_user: CurrentUser):
    if current_user.role == UserRole.PLACEMENT_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Placement Officers do not have clearance to access academic intervention data.",
        )


def _get_student_profile_for_user(db: Session, user_id: uuid.UUID, institution_id: uuid.UUID) -> StudentAcademicProfile:
    student = (
        db.query(StudentAcademicProfile)
        .filter(
            StudentAcademicProfile.profile_id == user_id,
            StudentAcademicProfile.institution_id == institution_id,
        )
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student academic profile not found for authenticated user")
    return student


# =========================================================================
# 1. Intervention Templates Endpoints
# =========================================================================

@router.get("/templates", response_model=List[InterventionTemplateResponse])
def get_intervention_templates(
    subject_id: Optional[uuid.UUID] = None,
    intervention_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    return intervention_template_service.get_templates(
        db=db,
        institution_id=inst_id,
        subject_id=subject_id,
        intervention_type=intervention_type,
    )


@router.post("/templates", response_model=InterventionTemplateResponse)
def create_intervention_template(
    payload: InterventionTemplateCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    return intervention_template_service.create_template(
        db=db,
        institution_id=inst_id,
        payload=payload,
        creator_id=user_id,
    )


# =========================================================================
# 2. Recommendations Endpoints
# =========================================================================

@router.post("/recommendations/generate", response_model=List[InterventionRecommendationResponse])
def generate_recommendations(
    payload: InterventionRecommendationGenerateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    recs = intervention_recommendation_service.generate_recommendations_for_student(
        db=db,
        institution_id=inst_id,
        student_id=payload.student_id,
        subject_id=payload.subject_id,
        topic_id=payload.topic_id,
        template_id=payload.template_id,
    )
    # Populate readable names for response
    results = []
    for r in recs:
        student = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == r.student_id).first()
        subj = db.query(AcademicSubject).filter(AcademicSubject.id == r.subject_id).first()
        topic = r.topic
        resp = InterventionRecommendationResponse.model_validate(r)
        if student:
            resp.student_name = f"{student.first_name} {student.last_name}"
            resp.enrollment_number = student.enrollment_number
        if subj:
            resp.subject_name = subj.name
            resp.subject_code = subj.code
        if topic:
            resp.topic_name = topic.topic_name
        results.append(resp)
    return results


@router.get("/recommendations", response_model=List[InterventionRecommendationResponse])
def get_recommendations(
    student_id: Optional[uuid.UUID] = None,
    subject_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)

    # Student can only query their own recommendations
    if current_user.role == UserRole.STUDENT:
        self_stud = _get_student_profile_for_user(db, user_id, inst_id)
        if student_id and student_id != self_stud.id:
            raise HTTPException(status_code=403, detail="Students may only view their own recommendations.")
        student_id = self_stud.id

    recs = intervention_recommendation_service.get_recommendations(
        db=db,
        institution_id=inst_id,
        student_id=student_id,
        subject_id=subject_id,
        status=status,
    )
    results = []
    for r in recs:
        student = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == r.student_id).first()
        subj = db.query(AcademicSubject).filter(AcademicSubject.id == r.subject_id).first()
        topic = r.topic
        resp = InterventionRecommendationResponse.model_validate(r)
        if student:
            resp.student_name = f"{student.first_name} {student.last_name}"
            resp.enrollment_number = student.enrollment_number
        if subj:
            resp.subject_name = subj.name
            resp.subject_code = subj.code
        if topic:
            resp.topic_name = topic.topic_name
        results.append(resp)
    return results


# =========================================================================
# 3. Intervention Plans Endpoints
# =========================================================================

@router.post("/plans", response_model=AcademicInterventionPlanResponse)
def create_intervention_plan(
    payload: InterventionPlanCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    plan = intervention_plan_service.create_plan(
        db=db,
        institution_id=inst_id,
        payload=payload,
        creator_id=user_id,
    )
    return _serialize_plan_response(db, plan)


@router.get("/plans", response_model=List[AcademicInterventionPlanResponse])
def list_intervention_plans(
    student_id: Optional[uuid.UUID] = None,
    subject_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)

    # Student isolation
    if current_user.role == UserRole.STUDENT:
        self_stud = _get_student_profile_for_user(db, user_id, inst_id)
        if student_id and student_id != self_stud.id:
            raise HTTPException(status_code=403, detail="Students may only view their own intervention plans.")
        student_id = self_stud.id

    plans = intervention_plan_service.list_plans(
        db=db,
        institution_id=inst_id,
        student_id=student_id,
        subject_id=subject_id,
        status=status,
    )
    return [_serialize_plan_response(db, p) for p in plans]


@router.get("/plans/{plan_id}", response_model=AcademicInterventionPlanResponse)
def get_intervention_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)

    plan = intervention_plan_service.get_plan_by_id(db, plan_id, inst_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Intervention plan not found")

    if current_user.role == UserRole.STUDENT:
        self_stud = _get_student_profile_for_user(db, user_id, inst_id)
        if plan.student_id != self_stud.id:
            raise HTTPException(status_code=403, detail="Students may only view their own intervention plans.")

    return _serialize_plan_response(db, plan)


@router.post("/plans/{plan_id}/review", response_model=AcademicInterventionPlanResponse)
def review_intervention_plan(
    plan_id: uuid.UUID,
    payload: InterventionPlanReviewRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    plan = intervention_plan_service.review_plan(
        db=db,
        institution_id=inst_id,
        plan_id=plan_id,
        reviewer_id=user_id,
        decision=payload.decision,
        review_notes=payload.review_notes,
        assigned_faculty_id=payload.assigned_faculty_id,
    )
    return _serialize_plan_response(db, plan)


@router.post("/plans/{plan_id}/assign", response_model=AcademicInterventionPlanResponse)
def assign_intervention_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    plan = intervention_plan_service.assign_plan(
        db=db,
        institution_id=inst_id,
        plan_id=plan_id,
        actor_id=user_id,
    )
    return _serialize_plan_response(db, plan)


# =========================================================================
# 4. Actions Endpoints
# =========================================================================

@router.post("/actions/{action_id}/status", response_model=InterventionActionResponse)
def update_action_status(
    action_id: uuid.UUID,
    payload: InterventionActionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    is_faculty = current_user.role in (UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN)

    # If student, verify that the action belongs to their plan
    if current_user.role == UserRole.STUDENT:
        self_stud = _get_student_profile_for_user(db, user_id, inst_id)
        action = (
            db.query(AcademicInterventionAction)
            .filter(
                AcademicInterventionAction.id == action_id,
                AcademicInterventionAction.institution_id == inst_id,
            )
            .first()
        )
        if not action or action.plan.student_id != self_stud.id:
            raise HTTPException(status_code=403, detail="You can only update actions assigned to yourself.")

    return intervention_plan_service.update_action_status(
        db=db,
        institution_id=inst_id,
        action_id=action_id,
        payload=payload,
        actor_id=user_id,
        is_faculty=is_faculty,
    )


# =========================================================================
# 5. Outcome Observations Endpoints
# =========================================================================

@router.post("/plans/{plan_id}/outcomes", response_model=InterventionOutcomeResponse)
def record_outcome_observation(
    plan_id: uuid.UUID,
    payload: InterventionOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return intervention_outcome_service.record_outcome_observation(
        db=db,
        institution_id=inst_id,
        plan_id=plan_id,
        payload=payload,
    )


@router.get("/plans/{plan_id}/outcomes", response_model=List[InterventionOutcomeResponse])
def get_outcome_observations(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _assert_not_placement_officer(current_user)
    inst_id = _parse_uuid(current_user.institution_id)
    return intervention_outcome_service.get_outcome_observations_for_plan(
        db=db,
        institution_id=inst_id,
        plan_id=plan_id,
    )


# =========================================================================
# 6. Dashboard Endpoints
# =========================================================================

@router.get("/dashboard/faculty", response_model=InterventionFacultyDashboardResponse)
def get_faculty_dashboard(
    subject_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    plans = intervention_plan_service.list_plans(db=db, institution_id=inst_id, subject_id=subject_id)
    recs = intervention_recommendation_service.get_recommendations(db=db, institution_id=inst_id, subject_id=subject_id, status="ACTIVE")

    total_plans = len(plans)
    active_count = sum(1 for p in plans if p.plan_status == InterventionPlanStatus.ACTIVE.value)
    draft_review_count = sum(1 for p in plans if p.plan_status in (InterventionPlanStatus.DRAFT.value, InterventionPlanStatus.PENDING_REVIEW.value))
    approved_assigned_count = sum(1 for p in plans if p.plan_status in (InterventionPlanStatus.APPROVED.value, InterventionPlanStatus.ACTIVE.value))
    completed_plans_count = sum(1 for p in plans if p.plan_status == InterventionPlanStatus.COMPLETED.value)
    
    # Overdue actions count
    now = datetime.now(timezone.utc)
    all_actions = (
        db.query(AcademicInterventionAction)
        .join(AcademicInterventionAction.plan)
        .filter(
            AcademicInterventionAction.institution_id == inst_id,
            AcademicInterventionAction.action_status.in_([InterventionActionStatus.ASSIGNED.value, InterventionActionStatus.IN_PROGRESS.value]),
            AcademicInterventionAction.due_date < now,
        )
        .all()
    )
    overdue_actions_count = len(all_actions)
    insufficient_ev_recs = sum(1 for r in recs if r.evidence_sufficiency == "INSUFFICIENT")

    return InterventionFacultyDashboardResponse(
        total_plans=total_plans,
        active_plans_count=active_count,
        draft_review_count=draft_review_count,
        approved_assigned_count=approved_assigned_count,
        completed_plans_count=completed_plans_count,
        overdue_actions_count=overdue_actions_count,
        insufficient_evidence_recommendations_count=insufficient_ev_recs,
        recent_plans=[_serialize_plan_response(db, p) for p in plans[:10]],
        active_recommendations=[
            InterventionRecommendationResponse.model_validate(r) for r in recs[:10]
        ],
        scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
    )


@router.get("/dashboard/student", response_model=InterventionStudentWorkspaceResponse)
def get_student_workspace(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.STUDENT])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    self_stud = _get_student_profile_for_user(db, user_id, inst_id)

    # Students only see APPROVED, ACTIVE, COMPLETED plans
    plans = (
        db.query(AcademicInterventionPlan)
        .filter(
            AcademicInterventionPlan.institution_id == inst_id,
            AcademicInterventionPlan.student_id == self_stud.id,
            AcademicInterventionPlan.plan_status.in_([
                InterventionPlanStatus.APPROVED.value,
                InterventionPlanStatus.ACTIVE.value,
                InterventionPlanStatus.COMPLETED.value,
            ]),
        )
        .order_by(AcademicInterventionPlan.created_at.desc())
        .all()
    )

    pending_actions = 0
    completed_actions = 0
    for p in plans:
        for act in p.actions:
            if act.action_status in (InterventionActionStatus.ASSIGNED.value, InterventionActionStatus.IN_PROGRESS.value):
                pending_actions += 1
            elif act.action_status == InterventionActionStatus.VERIFIED.value:
                completed_actions += 1

    return InterventionStudentWorkspaceResponse(
        student_id=self_stud.id,
        student_name=f"{self_stud.first_name} {self_stud.last_name}",
        active_plans=[_serialize_plan_response(db, p) for p in plans],
        pending_actions_count=pending_actions,
        completed_actions_count=completed_actions,
        scientific_disclaimer=DEFAULT_INTERVENTION_DISCLAIMER,
    )


# -------------------------------------------------------------------------
# Serialization Helper
# -------------------------------------------------------------------------

def _serialize_plan_response(db: Session, plan: AcademicInterventionPlan) -> AcademicInterventionPlanResponse:
    student = plan.student
    subj = plan.subject
    topic = plan.topic
    assigned_fac = plan.assigned_faculty

    resp = AcademicInterventionPlanResponse.model_validate(plan)
    if student:
        resp.student_name = f"{student.first_name} {student.last_name}"
        resp.enrollment_number = student.enrollment_number
    if subj:
        resp.subject_name = subj.name
        resp.subject_code = subj.code
    if topic:
        resp.topic_name = topic.topic_name
    if assigned_fac:
        resp.assigned_faculty_name = assigned_fac.full_name

    # Include actor names in progress events
    for ev in resp.progress_events:
        profile = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == ev.actor_profile_id).first()
        if not profile:
            from app.models.profile import Profile
            prof = db.query(Profile).filter(Profile.id == ev.actor_profile_id).first()
            if prof:
                ev.actor_name = prof.full_name

    return resp
