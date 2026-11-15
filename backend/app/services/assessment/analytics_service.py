import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.models.academic_data import (
    AcademicAssessment,
    StudentSubjectEnrollment,
)
from app.models.assessment import (
    AssessmentAttempt,
    AssessmentResponse,
    AssessmentQuestionMapping,
    AssessmentLearningOutcomeMapping,
)
from app.models.syllabus import LearningOutcome
from app.models.enums import AttemptStatus
from app.schemas.assessment import (
    AssessmentAnalyticsResponse,
    QuestionAnalyticsItem,
)


class AssessmentAnalyticsService:
    @staticmethod
    def get_assessment_analytics(
        db: Session,
        institution_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentAnalyticsResponse:
        asmt = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.id == assessment_id,
                AcademicAssessment.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not asmt:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found.",
            )

        # Enrolled students count
        total_enrolled = db.execute(
            select(func.count(StudentSubjectEnrollment.id)).where(
                StudentSubjectEnrollment.subject_id == asmt.subject_id,
                StudentSubjectEnrollment.institution_id == institution_id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE",
            )
        ).scalar() or 0

        # Attempts
        attempts = db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalars().all()

        total_attempts = len(attempts)
        completed = [a for a in attempts if a.attempt_status in [AttemptStatus.SUBMITTED.value, AttemptStatus.EVALUATED.value]]
        evaluated = [a for a in attempts if a.attempt_status == AttemptStatus.EVALUATED.value and a.marks_obtained is not None]
        pending = len(completed) - len(evaluated)

        scores = [a.marks_obtained for a in evaluated if a.marks_obtained is not None]
        avg_score = round(sum(scores) / len(scores), 2) if scores else None
        high_score = max(scores) if scores else None
        low_score = min(scores) if scores else None

        pass_rate = None
        if scores and asmt.passing_marks is not None:
            passed_count = sum(1 for s in scores if s >= asmt.passing_marks)
            pass_rate = round((passed_count / len(scores)) * 100.0, 1)

        # Question analytics
        mappings = db.execute(
            select(AssessmentQuestionMapping)
            .where(AssessmentQuestionMapping.assessment_id == assessment_id)
            .order_by(AssessmentQuestionMapping.display_order.asc())
        ).scalars().all()

        question_analytics: List[QuestionAnalyticsItem] = []
        for m in mappings:
            q = m.question
            responses = db.execute(
                select(AssessmentResponse).where(
                    AssessmentResponse.question_id == q.id,
                    AssessmentResponse.attempt_id.in_([a.id for a in completed]),
                )
            ).scalars().all()

            q_attempts = len(responses)
            correct_cnt = 0
            incorrect_cnt = 0
            part_cnt = 0
            awarded_marks_list = []

            for r in responses:
                if r.marks_awarded is not None:
                    awarded_marks_list.append(r.marks_awarded)
                    if r.marks_awarded >= m.marks_allocated:
                        correct_cnt += 1
                    elif r.marks_awarded > 0:
                        part_cnt += 1
                    else:
                        incorrect_cnt += 1

            avg_m = round(sum(awarded_marks_list) / len(awarded_marks_list), 2) if awarded_marks_list else 0.0
            succ_rate = round((correct_cnt / q_attempts) * 100.0, 1) if q_attempts > 0 else 0.0

            question_analytics.append(
                QuestionAnalyticsItem(
                    question_id=q.id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    difficulty=q.difficulty,
                    bloom_level=q.bloom_level,
                    allocated_marks=m.marks_allocated,
                    total_attempts=q_attempts,
                    correct_count=correct_cnt,
                    incorrect_count=incorrect_cnt,
                    partially_correct_count=part_cnt,
                    average_marks=avg_m,
                    success_rate_percentage=succ_rate,
                )
            )

        # Outcome coverage
        lo_mappings = db.execute(
            select(AssessmentLearningOutcomeMapping)
            .where(AssessmentLearningOutcomeMapping.assessment_id == assessment_id)
        ).scalars().all()

        outcome_coverage: List[Dict[str, Any]] = []
        for lom in lo_mappings:
            lo = lom.learning_outcome
            outcome_coverage.append({
                "learning_outcome_id": str(lo.id),
                "outcome_code": lo.outcome_code,
                "description": lo.description,
                "bloom_level": lo.bloom_level,
                "mapped_marks": lom.mapped_marks,
                "coverage_percentage": round((lom.mapped_marks / asmt.maximum_marks) * 100.0, 1) if lom.mapped_marks and asmt.maximum_marks else None,
            })

        return AssessmentAnalyticsResponse(
            assessment_id=asmt.id,
            assessment_name=asmt.assessment_name,
            maximum_marks=asmt.maximum_marks,
            total_enrolled_students=total_enrolled,
            total_attempts=total_attempts,
            completed_submissions=len(completed),
            evaluated_submissions=len(evaluated),
            pending_evaluations=pending,
            average_score=avg_score,
            highest_score=high_score,
            lowest_score=low_score,
            pass_rate_percentage=pass_rate,
            questions=question_analytics,
            outcome_coverage=outcome_coverage,
        )
