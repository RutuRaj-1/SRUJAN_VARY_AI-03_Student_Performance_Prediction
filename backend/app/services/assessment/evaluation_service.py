import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.academic_data import (
    AcademicAssessment,
    StudentAcademicProfile,
    StudentAssessmentRecord,
    AcademicRecordAudit,
)
from app.models.assessment import (
    AssessmentAttempt,
    AssessmentResponse,
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentQuestionMapping,
)
from app.models.enums import (
    AssessmentType,
    AttemptStatus,
    ResponseEvaluationStatus,
    QuestionType,
    AssessmentResultStatus,
    RecordVerificationStatus,
)
from app.schemas.assessment import BatchEvaluationRequest
from app.core.logging import logger


class EvaluationService:
    @staticmethod
    def evaluate_attempt_auto(
        db: Session,
        attempt: AssessmentAttempt,
    ) -> AssessmentAttempt:
        """
        Executes deterministic automated grading for objective questions (MCQ, Multi-select, True/False).
        Marks subjective or descriptive questions as FACULTY_REVIEW_REQUIRED.
        """
        asmt = attempt.assessment
        mappings = {
            m.question_id: m.marks_allocated
            for m in asmt.question_mappings
        }

        responses = db.execute(
            select(AssessmentResponse).where(AssessmentResponse.attempt_id == attempt.id)
        ).scalars().all()

        total_obtained = 0.0
        pending_faculty_review = False

        for resp in responses:
            question = resp.question
            allocated_marks = mappings.get(question.id, question.default_marks)
            payload = resp.response_payload or {}

            # 1. Multiple Choice Question (Single Select)
            if question.question_type == QuestionType.MCQ.value:
                selected_ids = payload.get("selected_option_ids", [])
                correct_opt = db.execute(
                    select(AssessmentQuestionOption).where(
                        AssessmentQuestionOption.question_id == question.id,
                        AssessmentQuestionOption.is_correct == True,
                    )
                ).scalar_one_or_none()

                if correct_opt and selected_ids and str(correct_opt.id) in [str(sid) for sid in selected_ids]:
                    resp.marks_awarded = allocated_marks
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "Correct option selected."
                else:
                    resp.marks_awarded = 0.0
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "Incorrect option selected."
                resp.is_auto_evaluated = True
                total_obtained += resp.marks_awarded

            # 2. True / False Question
            elif question.question_type == QuestionType.TRUE_FALSE.value:
                selected_ids = payload.get("selected_option_ids", [])
                correct_opt = db.execute(
                    select(AssessmentQuestionOption).where(
                        AssessmentQuestionOption.question_id == question.id,
                        AssessmentQuestionOption.is_correct == True,
                    )
                ).scalar_one_or_none()

                if correct_opt and selected_ids and str(correct_opt.id) in [str(sid) for sid in selected_ids]:
                    resp.marks_awarded = allocated_marks
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "Correct."
                else:
                    resp.marks_awarded = 0.0
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "Incorrect."
                resp.is_auto_evaluated = True
                total_obtained += resp.marks_awarded

            # 3. Multi-Select Question
            elif question.question_type == QuestionType.MULTI_SELECT.value:
                selected_ids = set(str(sid) for sid in payload.get("selected_option_ids", []))
                correct_opts = db.execute(
                    select(AssessmentQuestionOption).where(
                        AssessmentQuestionOption.question_id == question.id,
                        AssessmentQuestionOption.is_correct == True,
                    )
                ).scalars().all()
                correct_ids = set(str(opt.id) for opt in correct_opts)

                if selected_ids == correct_ids and len(correct_ids) > 0:
                    resp.marks_awarded = allocated_marks
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "All correct options identified."
                elif selected_ids.issubset(correct_ids) and len(selected_ids) > 0:
                    # Partial credit proportionate to correct selections
                    ratio = len(selected_ids) / len(correct_ids)
                    resp.marks_awarded = round(allocated_marks * ratio, 2)
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = f"Partially correct ({len(selected_ids)}/{len(correct_ids)} selected)."
                else:
                    resp.marks_awarded = 0.0
                    resp.evaluation_status = ResponseEvaluationStatus.AUTO_EVALUATED.value
                    resp.feedback = "Incorrect or invalid selection."
                resp.is_auto_evaluated = True
                total_obtained += resp.marks_awarded

            # 4. Descriptive, Coding or Rubric Questions
            else:
                resp.evaluation_status = ResponseEvaluationStatus.FACULTY_REVIEW_REQUIRED.value
                resp.marks_awarded = None
                resp.is_auto_evaluated = False
                pending_faculty_review = True

        attempt.marks_obtained = round(total_obtained, 2)
        if pending_faculty_review:
            attempt.attempt_status = AttemptStatus.UNDER_EVALUATION.value
            attempt.evaluation_status = "FACULTY_REVIEW_REQUIRED"
        else:
            attempt.attempt_status = AttemptStatus.EVALUATED.value
            attempt.evaluation_status = "AUTO_EVALUATED"

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def evaluate_submission_manually(
        db: Session,
        institution_id: uuid.UUID,
        faculty_id: uuid.UUID,
        attempt_id: uuid.UUID,
        payload: BatchEvaluationRequest,
    ) -> AssessmentAttempt:
        attempt = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment attempt not found.",
            )

        now = datetime.now(timezone.utc)
        mappings = {
            m.question_id: m.marks_allocated
            for m in attempt.assessment.question_mappings
        }

        for item in payload.evaluations:
            resp = db.execute(
                select(AssessmentResponse).where(
                    AssessmentResponse.attempt_id == attempt_id,
                    AssessmentResponse.question_id == item.question_id,
                )
            ).scalar_one_or_none()

            if not resp:
                continue

            max_alloc = mappings.get(item.question_id, resp.question.default_marks)
            if item.marks_awarded > max_alloc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Awarded marks ({item.marks_awarded}) exceed maximum allocated marks ({max_alloc}) for this question.",
                )

            resp.marks_awarded = item.marks_awarded
            resp.feedback = item.feedback
            resp.evaluator_id = faculty_id
            resp.evaluated_at = now
            resp.evaluation_status = ResponseEvaluationStatus.FACULTY_VERIFIED.value

        # Re-tally total marks
        all_responses = db.execute(
            select(AssessmentResponse).where(AssessmentResponse.attempt_id == attempt_id)
        ).scalars().all()

        total = 0.0
        all_evaluated = True
        for r in all_responses:
            if r.marks_awarded is not None:
                total += r.marks_awarded
            else:
                all_evaluated = False

        attempt.marks_obtained = round(total, 2)
        if all_evaluated:
            attempt.attempt_status = AttemptStatus.EVALUATED.value
            attempt.evaluation_status = "FACULTY_EVALUATED"

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def verify_and_release_result(
        db: Session,
        institution_id: uuid.UUID,
        faculty_id: uuid.UUID,
        attempt_id: uuid.UUID,
        publish_to_official_records: bool = True,
        verification_remarks: Optional[str] = "Online Assessment verified by Faculty",
    ) -> AssessmentAttempt:
        attempt = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == attempt_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment attempt not found.",
            )

        if attempt.marks_obtained is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attempt must be evaluated before releasing verified results.",
            )

        asmt = attempt.assessment
        now = datetime.now(timezone.utc)
        attempt.evaluation_status = "FACULTY_VERIFIED"

        # Check if this assessment should publish an official academic performance record (Phase 04 Integration)
        is_practice = (asmt.assessment_type == AssessmentType.PRACTICE_TEST.value)
        if publish_to_official_records and not is_practice:
            # Determine PASSED / FAILED based on passing_marks
            pass_status = AssessmentResultStatus.PASSED.value
            if asmt.passing_marks is not None and attempt.marks_obtained < asmt.passing_marks:
                pass_status = AssessmentResultStatus.FAILED.value

            # Check if record already exists in Phase 04 student_assessment_records
            existing_record = db.execute(
                select(StudentAssessmentRecord).where(
                    StudentAssessmentRecord.assessment_id == asmt.id,
                    StudentAssessmentRecord.student_id == attempt.student_id,
                )
            ).scalar_one_or_none()

            if existing_record:
                old_val = {"marks_obtained": existing_record.marks_obtained, "verification_status": existing_record.verification_status}
                existing_record.marks_obtained = attempt.marks_obtained
                existing_record.result_status = pass_status
                existing_record.verification_status = RecordVerificationStatus.VERIFIED.value
                existing_record.verified_by = faculty_id
                existing_record.verified_at = now
                existing_record.remarks = verification_remarks
                new_val = {"marks_obtained": existing_record.marks_obtained, "verification_status": existing_record.verification_status}

                # Audit trail
                db.add(AcademicRecordAudit(
                    institution_id=institution_id,
                    entity_type="student_assessment_records",
                    entity_id=existing_record.id,
                    action="UPDATE_VERIFIED_MARKS",
                    actor_id=faculty_id,
                    before_state=old_val,
                    after_state=new_val,
                    reason=verification_remarks,
                ))
            else:
                new_record = StudentAssessmentRecord(
                    institution_id=institution_id,
                    student_id=attempt.student_id,
                    assessment_id=asmt.id,
                    marks_obtained=attempt.marks_obtained,
                    maximum_marks_snapshot=asmt.maximum_marks,
                    result_status=pass_status,
                    source_type="ONLINE_ASSESSMENT",
                    verification_status=RecordVerificationStatus.VERIFIED.value,
                    recorded_by=faculty_id,
                    verified_by=faculty_id,
                    recorded_at=now,
                    verified_at=now,
                    remarks=verification_remarks,
                )
                db.add(new_record)
                db.flush()

                # Audit trail
                db.add(AcademicRecordAudit(
                    institution_id=institution_id,
                    entity_type="student_assessment_records",
                    entity_id=new_record.id,
                    action="CREATE_VERIFIED_MARKS",
                    actor_id=faculty_id,
                    before_state=None,
                    after_state={"marks_obtained": new_record.marks_obtained, "verification_status": "VERIFIED"},
                    reason=verification_remarks,
                ))

            logger.info("Published official academic record for student %s on assessment %s", attempt.student_id, asmt.id)

        db.commit()
        db.refresh(attempt)
        return attempt
