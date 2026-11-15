import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser, require_roles
from app.models.enums import UserRole, QuestionType, QuestionDifficulty
from app.models.academic_data import AcademicAssessment, StudentAcademicProfile
from app.models.assessment import AssessmentAttempt, AssessmentResponse, AssessmentQuestion
from app.schemas.assessment import (
    QuestionCreate,
    QuestionUpdate,
    QuestionDetailResponse,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentDetailResponse,
    AttemptStartResponse,
    AttemptDetailResponse,
    ResponseSaveRequest,
    ResponseItemDetail,
    BatchEvaluationRequest,
    ReleaseResultRequest,
    EngagementEventCreate,
    EngagementEventResponse,
    LearningEngagementSummary,
    AssessmentAnalyticsResponse,
)
from app.services.assessment.question_service import QuestionService
from app.services.assessment.delivery_service import AssessmentDeliveryService
from app.services.assessment.evaluation_service import EvaluationService
from app.services.assessment.engagement_service import EngagementService
from app.services.assessment.analytics_service import AssessmentAnalyticsService

router = APIRouter()


# ==========================================================
# Question Bank Endpoints
# ==========================================================

@router.post("/questions", response_model=QuestionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    creator_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return QuestionService.create_question(db, inst_id, creator_id, payload)


@router.get("/questions", response_model=List[QuestionDetailResponse])
def list_questions(
    subject_id: Optional[uuid.UUID] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    learning_outcome_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return QuestionService.get_questions(
        db, inst_id, subject_id, difficulty, question_type, learning_outcome_id, search, skip, limit
    )


@router.get("/questions/{question_id}", response_model=QuestionDetailResponse)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return QuestionService.get_question_by_id(db, inst_id, question_id)


@router.patch("/questions/{question_id}", response_model=QuestionDetailResponse)
def update_question(
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return QuestionService.update_question(db, inst_id, question_id, payload)


@router.post("/questions/generate-drafts", response_model=List[QuestionDetailResponse])
def generate_draft_questions(
    subject_id: uuid.UUID,
    topic_id: Optional[uuid.UUID] = None,
    learning_outcome_id: Optional[uuid.UUID] = None,
    count: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return QuestionService.generate_draft_questions_ai(
        db, inst_id, subject_id, topic_id, learning_outcome_id, count
    )


# ==========================================================
# Assessment Management Endpoints
# ==========================================================

@router.post("", response_model=AssessmentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    creator_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    asmt = AssessmentDeliveryService.create_assessment(db, inst_id, creator_id, payload)

    total_marks = sum(m.marks_allocated for m in asmt.question_mappings)
    return AssessmentDetailResponse(
        id=asmt.id,
        institution_id=asmt.institution_id,
        subject_id=asmt.subject_id,
        academic_year=asmt.academic_year,
        semester=asmt.semester,
        assessment_name=asmt.assessment_name,
        assessment_type=asmt.assessment_type,
        maximum_marks=asmt.maximum_marks,
        passing_marks=asmt.passing_marks,
        weightage_percentage=asmt.weightage_percentage,
        description=asmt.description,
        instructions=asmt.instructions,
        is_online_assessment=asmt.is_online_assessment,
        duration_minutes=asmt.duration_minutes,
        start_time=asmt.start_time,
        end_time=asmt.end_time,
        evaluation_mode=asmt.evaluation_mode,
        attempt_limit=asmt.attempt_limit,
        allow_review=asmt.allow_review,
        status=asmt.status,
        created_at=asmt.created_at,
        updated_at=asmt.updated_at,
        question_count=len(asmt.question_mappings),
        total_configured_marks=total_marks,
    )


@router.get("", response_model=List[AssessmentDetailResponse])
def list_assessments(
    subject_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    query = select(AcademicAssessment).where(AcademicAssessment.institution_id == inst_id)

    if subject_id:
        query = query.where(AcademicAssessment.subject_id == subject_id)
    if status_filter:
        query = query.where(AcademicAssessment.status == status_filter)

    query = query.order_by(AcademicAssessment.created_at.desc())
    asmts = list(db.execute(query).scalars().all())

    results = []
    for asmt in asmts:
        total_marks = sum(m.marks_allocated for m in asmt.question_mappings)
        results.append(
            AssessmentDetailResponse(
                id=asmt.id,
                institution_id=asmt.institution_id,
                subject_id=asmt.subject_id,
                academic_year=asmt.academic_year,
                semester=asmt.semester,
                assessment_name=asmt.assessment_name,
                assessment_type=asmt.assessment_type,
                maximum_marks=asmt.maximum_marks,
                passing_marks=asmt.passing_marks,
                weightage_percentage=asmt.weightage_percentage,
                description=asmt.description,
                instructions=asmt.instructions,
                is_online_assessment=asmt.is_online_assessment,
                duration_minutes=asmt.duration_minutes,
                start_time=asmt.start_time,
                end_time=asmt.end_time,
                evaluation_mode=asmt.evaluation_mode,
                attempt_limit=asmt.attempt_limit,
                allow_review=asmt.allow_review,
                status=asmt.status,
                created_at=asmt.created_at,
                updated_at=asmt.updated_at,
                question_count=len(asmt.question_mappings),
                total_configured_marks=total_marks,
            )
        )
    return results


@router.get("/available", response_model=List[Dict[str, Any]])
def get_available_assessments(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    # Find student profile
    student = db.execute(
        select(StudentAcademicProfile).where(
            StudentAcademicProfile.institution_id == inst_id,
            StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
        )
    ).scalar_one_or_none()

    if not student:
        # If user is faculty or admin, find or allow test
        student = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).first()
        if student:
            student = student[0]
        else:
            return []

    return AssessmentDeliveryService.get_available_assessments_for_student(db, inst_id, student.id)


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    asmt = db.execute(
        select(AcademicAssessment).where(
            AcademicAssessment.id == assessment_id,
            AcademicAssessment.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not asmt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    total_marks = sum(m.marks_allocated for m in asmt.question_mappings)
    return AssessmentDetailResponse(
        id=asmt.id,
        institution_id=asmt.institution_id,
        subject_id=asmt.subject_id,
        academic_year=asmt.academic_year,
        semester=asmt.semester,
        assessment_name=asmt.assessment_name,
        assessment_type=asmt.assessment_type,
        maximum_marks=asmt.maximum_marks,
        passing_marks=asmt.passing_marks,
        weightage_percentage=asmt.weightage_percentage,
        description=asmt.description,
        instructions=asmt.instructions,
        is_online_assessment=asmt.is_online_assessment,
        duration_minutes=asmt.duration_minutes,
        start_time=asmt.start_time,
        end_time=asmt.end_time,
        evaluation_mode=asmt.evaluation_mode,
        attempt_limit=asmt.attempt_limit,
        allow_review=asmt.allow_review,
        status=asmt.status,
        created_at=asmt.created_at,
        updated_at=asmt.updated_at,
        question_count=len(asmt.question_mappings),
        total_configured_marks=total_marks,
    )


@router.post("/{assessment_id}/publish", response_model=AssessmentDetailResponse)
def publish_assessment(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    asmt = AssessmentDeliveryService.publish_assessment(db, inst_id, assessment_id)
    total_marks = sum(m.marks_allocated for m in asmt.question_mappings)
    return AssessmentDetailResponse(
        id=asmt.id,
        institution_id=asmt.institution_id,
        subject_id=asmt.subject_id,
        academic_year=asmt.academic_year,
        semester=asmt.semester,
        assessment_name=asmt.assessment_name,
        assessment_type=asmt.assessment_type,
        maximum_marks=asmt.maximum_marks,
        passing_marks=asmt.passing_marks,
        weightage_percentage=asmt.weightage_percentage,
        description=asmt.description,
        instructions=asmt.instructions,
        is_online_assessment=asmt.is_online_assessment,
        duration_minutes=asmt.duration_minutes,
        start_time=asmt.start_time,
        end_time=asmt.end_time,
        evaluation_mode=asmt.evaluation_mode,
        attempt_limit=asmt.attempt_limit,
        allow_review=asmt.allow_review,
        status=asmt.status,
        created_at=asmt.created_at,
        updated_at=asmt.updated_at,
        question_count=len(asmt.question_mappings),
        total_configured_marks=total_marks,
    )


# ==========================================================
# Student Assessment Attempt Endpoints
# ==========================================================

@router.post("/{assessment_id}/attempts", response_model=AttemptStartResponse)
def start_assessment_attempt(
    assessment_id: uuid.UUID,
    student_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)

    # Determine student target
    target_student_id = student_id
    if not target_student_id:
        stud_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.institution_id == inst_id,
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
            )
        ).scalar_one_or_none()
        if stud_prof:
            target_student_id = stud_prof.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student profile not linked to current user.",
            )

    return AssessmentDeliveryService.start_attempt(db, inst_id, target_student_id, assessment_id)


@router.put("/attempts/{attempt_id}/responses", response_model=ResponseItemDetail)
def save_student_response(
    attempt_id: uuid.UUID,
    payload: ResponseSaveRequest,
    student_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    target_student_id = student_id
    if not target_student_id:
        stud_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.institution_id == inst_id,
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
            )
        ).scalar_one_or_none()
        if stud_prof:
            target_student_id = stud_prof.id
        else:
            # Fallback for attempt owner lookup
            att = db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id)).scalar_one_or_none()
            if att:
                target_student_id = att.student_id
            else:
                raise HTTPException(status_code=404, detail="Attempt not found.")

    resp = AssessmentDeliveryService.save_response(db, inst_id, target_student_id, attempt_id, payload)
    return resp


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptDetailResponse)
def submit_student_attempt(
    attempt_id: uuid.UUID,
    student_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    target_student_id = student_id
    if not target_student_id:
        stud_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.institution_id == inst_id,
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
            )
        ).scalar_one_or_none()
        if stud_prof:
            target_student_id = stud_prof.id
        else:
            att = db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id)).scalar_one_or_none()
            if att:
                target_student_id = att.student_id
            else:
                raise HTTPException(status_code=404, detail="Attempt not found.")

    return AssessmentDeliveryService.submit_attempt(db, inst_id, target_student_id, attempt_id)


@router.get("/attempts/{attempt_id}", response_model=AttemptDetailResponse)
def get_attempt_detail(
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    att = db.execute(
        select(AssessmentAttempt).where(
            AssessmentAttempt.id == attempt_id,
            AssessmentAttempt.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not att:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment attempt not found.",
        )
    return att


# ==========================================================
# Faculty Evaluation & Review Endpoints
# ==========================================================

@router.get("/{assessment_id}/submissions", response_model=List[AttemptDetailResponse])
def list_assessment_submissions(
    assessment_id: uuid.UUID,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    query = select(AssessmentAttempt).where(
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.institution_id == inst_id,
    )
    if status_filter:
        query = query.where(AssessmentAttempt.attempt_status == status_filter)

    query = query.order_by(AssessmentAttempt.submitted_at.desc())
    return list(db.execute(query).scalars().all())


@router.get("/submissions/{attempt_id}", response_model=AttemptDetailResponse)
def get_submission_for_evaluation(
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    att = db.execute(
        select(AssessmentAttempt).where(
            AssessmentAttempt.id == attempt_id,
            AssessmentAttempt.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not att:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return att


@router.post("/submissions/{attempt_id}/evaluate", response_model=AttemptDetailResponse)
def evaluate_submission_manually(
    attempt_id: uuid.UUID,
    payload: BatchEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    faculty_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return EvaluationService.evaluate_submission_manually(
        db, inst_id, faculty_id, attempt_id, payload
    )


@router.post("/submissions/{attempt_id}/release-result", response_model=AttemptDetailResponse)
def release_verified_result(
    attempt_id: uuid.UUID,
    payload: ReleaseResultRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    faculty_id = uuid.UUID(current_user.user_id) if current_user.user_id else None
    return EvaluationService.verify_and_release_result(
        db,
        inst_id,
        faculty_id,
        attempt_id,
        payload.publish_to_official_records,
        payload.verification_remarks,
    )


# ==========================================================
# Learning Engagement & Analytics Endpoints
# ==========================================================

@router.post("/engagement/events", response_model=EngagementEventResponse, status_code=status.HTTP_201_CREATED)
def record_engagement_event(
    payload: EngagementEventCreate,
    student_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    target_student_id = student_id
    if not target_student_id:
        stud_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.institution_id == inst_id,
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
            )
        ).scalar_one_or_none()
        if stud_prof:
            target_student_id = stud_prof.id
        else:
            raise HTTPException(status_code=400, detail="Student profile not found for engagement event.")

    event = EngagementService.record_event(
        db=db,
        institution_id=inst_id,
        student_id=target_student_id,
        assessment_id=payload.assessment_id,
        attempt_id=payload.attempt_id,
        event_type=payload.event_type.value if hasattr(payload.event_type, 'value') else payload.event_type,
        metadata=payload.event_metadata,
        source=payload.source,
    )
    db.commit()
    db.refresh(event)
    return event


@router.get("/{assessment_id}/engagement-summary", response_model=LearningEngagementSummary)
def get_engagement_summary(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return EngagementService.get_assessment_engagement_summary(db, inst_id, assessment_id)


@router.get("/{assessment_id}/analytics", response_model=AssessmentAnalyticsResponse)
def get_assessment_analytics(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    return AssessmentAnalyticsService.get_assessment_analytics(db, inst_id, assessment_id)
