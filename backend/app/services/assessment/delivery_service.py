import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.academic_data import (
    AcademicAssessment,
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    StudentAssessmentRecord,
)
from app.models.assessment import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentQuestionMapping,
    AssessmentLearningOutcomeMapping,
    AssessmentAttempt,
    AssessmentResponse,
    LearningEngagementEvent,
)
from app.models.syllabus import AcademicSubject, LearningOutcome
from app.models.enums import (
    AssessmentType,
    AttemptStatus,
    ResponseEvaluationStatus,
    LearningEngagementEventType,
    QuestionType,
)
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AttemptStartResponse,
    StudentQuestionView,
    StudentQuestionOptionResponse,
    ResponseSaveRequest,
)
from app.services.assessment.evaluation_service import EvaluationService
from app.services.assessment.engagement_service import EngagementService
from app.core.logging import logger


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class AssessmentDeliveryService:
    @staticmethod
    def create_assessment(
        db: Session,
        institution_id: uuid.UUID,
        creator_id: Optional[uuid.UUID],
        payload: AssessmentCreate,
    ) -> AcademicAssessment:
        # 1. Verify subject belongs to institution
        subject = db.execute(
            select(AcademicSubject).where(
                AcademicSubject.id == payload.subject_id,
                AcademicSubject.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic subject not found in your institution.",
            )

        # 2. Check unique assessment name per subject and term
        existing = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.subject_id == payload.subject_id,
                AcademicAssessment.academic_year == payload.academic_year,
                AcademicAssessment.semester == payload.semester,
                AcademicAssessment.assessment_name == payload.assessment_name,
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An assessment named '{payload.assessment_name}' already exists for this subject and term.",
            )

        # 3. Create Assessment entity
        assessment = AcademicAssessment(
            institution_id=institution_id,
            subject_id=payload.subject_id,
            academic_year=payload.academic_year,
            semester=payload.semester,
            assessment_name=payload.assessment_name,
            assessment_type=payload.assessment_type.value if hasattr(payload.assessment_type, 'value') else payload.assessment_type,
            maximum_marks=payload.maximum_marks,
            passing_marks=payload.passing_marks,
            weightage_percentage=payload.weightage_percentage,
            description=payload.description,
            instructions=payload.instructions,
            is_online_assessment=payload.is_online_assessment,
            duration_minutes=payload.duration_minutes,
            start_time=payload.start_time,
            end_time=payload.end_time,
            evaluation_mode=payload.evaluation_mode.value if hasattr(payload.evaluation_mode, 'value') else payload.evaluation_mode,
            attempt_limit=payload.attempt_limit,
            allow_review=payload.allow_review,
            created_by=creator_id,
            status="DRAFT",
        )
        db.add(assessment)
        db.flush()

        # 4. Attach question mappings if provided
        total_mapped_marks = 0.0
        if payload.questions:
            for item in payload.questions:
                # Verify question belongs to institution
                q = db.execute(
                    select(AssessmentQuestion).where(
                        AssessmentQuestion.id == item.question_id,
                        AssessmentQuestion.institution_id == institution_id,
                    )
                ).scalar_one_or_none()
                if not q:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Question {item.question_id} not found in this institution.",
                    )

                mapping = AssessmentQuestionMapping(
                    assessment_id=assessment.id,
                    question_id=item.question_id,
                    marks_allocated=item.marks_allocated,
                    display_order=item.display_order,
                    required=item.required,
                )
                db.add(mapping)
                total_mapped_marks += item.marks_allocated

            # Validation: Warn or check if total marks match maximum marks
            if abs(total_mapped_marks - payload.maximum_marks) > 0.01:
                logger.info(
                    "Configured question marks (%.2f) differ from assessment maximum marks (%.2f).",
                    total_mapped_marks, payload.maximum_marks
                )

        # 5. Attach outcome mappings if provided
        if payload.outcome_mappings:
            for out_item in payload.outcome_mappings:
                lo_mapping = AssessmentLearningOutcomeMapping(
                    institution_id=institution_id,
                    assessment_id=assessment.id,
                    learning_outcome_id=out_item.learning_outcome_id,
                    competency_id=out_item.competency_id,
                    mapped_marks=out_item.mapped_marks,
                    created_by=creator_id,
                )
                db.add(lo_mapping)

        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def publish_assessment(
        db: Session,
        institution_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AcademicAssessment:
        assessment = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.id == assessment_id,
                AcademicAssessment.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found.",
            )

        if not assessment.question_mappings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish an assessment with zero configured questions.",
            )

        assessment.status = "PUBLISHED"
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def get_available_assessments_for_student(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> List[Dict[str, Any]]:
        # 1. Fetch student enrolled subject IDs
        enrolled_subject_ids = db.execute(
            select(StudentSubjectEnrollment.subject_id).where(
                StudentSubjectEnrollment.student_id == student_id,
                StudentSubjectEnrollment.institution_id == institution_id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE",
            )
        ).scalars().all()
        if not enrolled_subject_ids:
            return []

        # 2. Query published assessments for enrolled subjects
        now = datetime.now(timezone.utc)
        assessments = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.institution_id == institution_id,
                AcademicAssessment.subject_id.in_(enrolled_subject_ids),
                AcademicAssessment.status == "PUBLISHED",
            ).order_by(AcademicAssessment.created_at.desc())
        ).scalars().all()

        results = []
        for asmt in assessments:
            # Check completed attempts
            completed_attempts = db.execute(
                select(func.count(AssessmentAttempt.id)).where(
                    AssessmentAttempt.assessment_id == asmt.id,
                    AssessmentAttempt.student_id == student_id,
                    AssessmentAttempt.attempt_status.in_([AttemptStatus.SUBMITTED.value, AttemptStatus.EVALUATED.value]),
                )
            ).scalar() or 0

            in_progress = db.execute(
                select(AssessmentAttempt).where(
                    AssessmentAttempt.assessment_id == asmt.id,
                    AssessmentAttempt.student_id == student_id,
                    AssessmentAttempt.attempt_status == AttemptStatus.IN_PROGRESS.value,
                )
            ).scalar_one_or_none()

            can_attempt = (completed_attempts < asmt.attempt_limit) or (in_progress is not None)

            # Check time window if defined
            is_window_active = True
            st = _ensure_utc(asmt.start_time)
            et = _ensure_utc(asmt.end_time)
            if st and now < st:
                is_window_active = False
            if et and now > et:
                is_window_active = False

            results.append({
                "assessment": {
                    "id": str(asmt.id),
                    "institution_id": str(asmt.institution_id),
                    "subject_id": str(asmt.subject_id),
                    "assessment_name": asmt.assessment_name,
                    "assessment_type": asmt.assessment_type,
                    "maximum_marks": asmt.maximum_marks,
                    "passing_marks": asmt.passing_marks,
                    "duration_minutes": asmt.duration_minutes,
                    "start_time": asmt.start_time.isoformat() if asmt.start_time else None,
                    "end_time": asmt.end_time.isoformat() if asmt.end_time else None,
                    "instructions": asmt.instructions,
                    "attempt_limit": asmt.attempt_limit,
                    "status": asmt.status,
                },
                "can_attempt": can_attempt and is_window_active,
                "completed_attempts": completed_attempts,
                "attempt_limit": asmt.attempt_limit,
                "active_attempt_id": str(in_progress.id) if in_progress else None,
                "is_window_active": is_window_active,
            })
        return results

    @staticmethod
    def start_attempt(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AttemptStartResponse:
        # 1. Fetch Assessment
        asmt = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.id == assessment_id,
                AcademicAssessment.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not asmt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found.",
            )

        if asmt.status != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This assessment is not open for student attempts.",
            )

        # 2. Validate Student Enrollment in this subject
        enrollment = db.execute(
            select(StudentSubjectEnrollment).where(
                StudentSubjectEnrollment.student_id == student_id,
                StudentSubjectEnrollment.subject_id == asmt.subject_id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE",
            )
        ).scalar_one_or_none()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not enrolled in the subject for this assessment.",
            )

        # 3. Check for existing active attempt (Resume capability)
        existing_attempt = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.student_id == student_id,
                AssessmentAttempt.attempt_status == AttemptStatus.IN_PROGRESS.value,
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing_attempt:
            # Check deadline expiration
            ex_deadline = _ensure_utc(existing_attempt.deadline_at)
            if ex_deadline and now > ex_deadline:
                existing_attempt.attempt_status = AttemptStatus.EXPIRED.value
                db.commit()
            else:
                # Log resume event and return questions
                EngagementService.record_event(
                    db=db,
                    institution_id=institution_id,
                    student_id=student_id,
                    assessment_id=assessment_id,
                    attempt_id=existing_attempt.id,
                    event_type=LearningEngagementEventType.ASSESSMENT_RESUMED.value,
                    metadata={"resumed_at": now.isoformat()},
                )
                return AssessmentDeliveryService._build_attempt_response(db, asmt, existing_attempt)

        # 4. Check Attempt Limits
        attempt_count = db.execute(
            select(func.count(AssessmentAttempt.id)).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.student_id == student_id,
            )
        ).scalar() or 0

        if attempt_count >= asmt.attempt_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have reached the maximum attempt limit ({asmt.attempt_limit}) for this assessment.",
            )

        # 5. Calculate Deadline
        deadline = None
        if asmt.duration_minutes:
            deadline = now + timedelta(minutes=asmt.duration_minutes)
            et = _ensure_utc(asmt.end_time)
            if et and deadline > et:
                deadline = et

        new_attempt = AssessmentAttempt(
            institution_id=institution_id,
            assessment_id=assessment_id,
            student_id=student_id,
            attempt_number=attempt_count + 1,
            attempt_status=AttemptStatus.IN_PROGRESS.value,
            started_at=now,
            deadline_at=deadline,
            total_marks=asmt.maximum_marks,
            marks_obtained=None,
            evaluation_status="NOT_EVALUATED",
        )
        db.add(new_attempt)
        db.flush()

        # 6. Record START event in engagement telemetry
        EngagementService.record_event(
            db=db,
            institution_id=institution_id,
            student_id=student_id,
            assessment_id=assessment_id,
            attempt_id=new_attempt.id,
            event_type=LearningEngagementEventType.ASSESSMENT_STARTED.value,
            metadata={"started_at": now.isoformat(), "attempt_number": new_attempt.attempt_number},
        )

        db.commit()
        db.refresh(new_attempt)
        return AssessmentDeliveryService._build_attempt_response(db, asmt, new_attempt)

    @staticmethod
    def _build_attempt_response(
        db: Session,
        asmt: AcademicAssessment,
        attempt: AssessmentAttempt,
    ) -> AttemptStartResponse:
        """Constructs student-facing questions securely WITHOUT is_correct or expected answers."""
        mappings = db.execute(
            select(AssessmentQuestionMapping)
            .where(AssessmentQuestionMapping.assessment_id == asmt.id)
            .order_by(AssessmentQuestionMapping.display_order.asc())
        ).scalars().all()

        questions_view: List[StudentQuestionView] = []
        for map_item in mappings:
            q = map_item.question
            options_view = [
                StudentQuestionOptionResponse(
                    id=opt.id,
                    option_text=opt.option_text,
                    display_order=opt.display_order,
                )
                for opt in q.options
            ]
            questions_view.append(
                StudentQuestionView(
                    id=q.id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    marks_allocated=map_item.marks_allocated,
                    display_order=map_item.display_order,
                    required=map_item.required,
                    code_language=q.code_language,
                    code_template=q.code_template,
                    options=options_view,
                )
            )

        return AttemptStartResponse(
            attempt_id=attempt.id,
            assessment_id=asmt.id,
            assessment_name=asmt.assessment_name,
            duration_minutes=asmt.duration_minutes,
            deadline_at=attempt.deadline_at,
            started_at=attempt.started_at,
            attempt_number=attempt.attempt_number,
            questions=questions_view,
        )

    @staticmethod
    def save_response(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        attempt_id: uuid.UUID,
        payload: ResponseSaveRequest,
    ) -> AssessmentResponse:
        attempt = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.student_id == student_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment attempt session not found.",
            )

        now = datetime.now(timezone.utc)
        if attempt.attempt_status != AttemptStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot save answers on an attempt with status {attempt.attempt_status}.",
            )

        att_deadline = _ensure_utc(attempt.deadline_at)
        if att_deadline and now > att_deadline:
            attempt.attempt_status = AttemptStatus.EXPIRED.value
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment time limit has expired. Responses can no longer be updated.",
            )

        # Check existing response
        existing_resp = db.execute(
            select(AssessmentResponse).where(
                AssessmentResponse.attempt_id == attempt_id,
                AssessmentResponse.question_id == payload.question_id,
            )
        ).scalar_one_or_none()

        if existing_resp:
            existing_resp.response_payload = payload.response_payload
            existing_resp.saved_at = now
            existing_resp.revision_count += 1
            db.commit()
            db.refresh(existing_resp)

            # Record ANSWER_REVISED telemetry
            EngagementService.record_event(
                db=db,
                institution_id=institution_id,
                student_id=student_id,
                assessment_id=attempt.assessment_id,
                attempt_id=attempt.id,
                event_type=LearningEngagementEventType.ANSWER_REVISED.value,
                metadata={"question_id": str(payload.question_id), "revision_count": existing_resp.revision_count},
            )
            return existing_resp

        # Create new response
        new_resp = AssessmentResponse(
            institution_id=institution_id,
            attempt_id=attempt_id,
            question_id=payload.question_id,
            response_payload=payload.response_payload,
            saved_at=now,
            revision_count=0,
            evaluation_status=ResponseEvaluationStatus.PENDING.value,
        )
        db.add(new_resp)
        db.commit()
        db.refresh(new_resp)

        # Record ANSWER_SAVED telemetry
        EngagementService.record_event(
            db=db,
            institution_id=institution_id,
            student_id=student_id,
            assessment_id=attempt.assessment_id,
            attempt_id=attempt.id,
            event_type=LearningEngagementEventType.ANSWER_SAVED.value,
            metadata={"question_id": str(payload.question_id)},
        )
        return new_resp

    @staticmethod
    def submit_attempt(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        attempt_id: uuid.UUID,
    ) -> AssessmentAttempt:
        attempt = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.student_id == student_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment attempt session not found.",
            )

        if attempt.attempt_status in [AttemptStatus.SUBMITTED.value, AttemptStatus.EVALUATED.value]:
            return attempt  # Idempotent return

        now = datetime.now(timezone.utc)
        attempt.submitted_at = now
        attempt.attempt_status = AttemptStatus.SUBMITTED.value
        db.commit()

        # Record ASSESSMENT_SUBMITTED telemetry
        EngagementService.record_event(
            db=db,
            institution_id=institution_id,
            student_id=student_id,
            assessment_id=attempt.assessment_id,
            attempt_id=attempt.id,
            event_type=LearningEngagementEventType.ASSESSMENT_SUBMITTED.value,
            metadata={"submitted_at": now.isoformat()},
        )

        # Trigger automatic evaluation for objective questions
        attempt = EvaluationService.evaluate_attempt_auto(db, attempt)
        return attempt
