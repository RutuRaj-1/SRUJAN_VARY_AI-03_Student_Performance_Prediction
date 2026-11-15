import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.assessment import (
    AssessmentQuestion,
    AssessmentQuestionOption,
)
from app.models.syllabus import AcademicSubject, SyllabusUnit, SyllabusTopic, LearningOutcome, Competency
from app.models.enums import (
    QuestionType,
    QuestionDifficulty,
    QuestionEvaluationMethod,
    BloomTaxonomyLevel,
)
from app.schemas.assessment import QuestionCreate, QuestionUpdate, QuestionOptionCreate
from app.core.logging import logger


class QuestionService:
    @staticmethod
    def create_question(
        db: Session,
        institution_id: uuid.UUID,
        creator_id: Optional[uuid.UUID],
        payload: QuestionCreate,
    ) -> AssessmentQuestion:
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

        # 2. Verify optional curriculum mappings
        if payload.learning_outcome_id:
            lo = db.execute(
                select(LearningOutcome).where(
                    LearningOutcome.id == payload.learning_outcome_id,
                    LearningOutcome.subject_id == payload.subject_id,
                )
            ).scalar_one_or_none()
            if not lo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified learning outcome is not part of this subject syllabus.",
                )

        # 3. Create Question record
        question = AssessmentQuestion(
            institution_id=institution_id,
            subject_id=payload.subject_id,
            unit_id=payload.unit_id,
            topic_id=payload.topic_id,
            learning_outcome_id=payload.learning_outcome_id,
            competency_id=payload.competency_id,
            question_text=payload.question_text,
            question_type=payload.question_type.value if hasattr(payload.question_type, 'value') else payload.question_type,
            difficulty=payload.difficulty.value if hasattr(payload.difficulty, 'value') else payload.difficulty,
            bloom_level=payload.bloom_level,
            default_marks=payload.default_marks,
            explanation=payload.explanation,
            expected_answer=payload.expected_answer,
            evaluation_method=payload.evaluation_method.value if hasattr(payload.evaluation_method, 'value') else payload.evaluation_method,
            code_language=payload.code_language,
            code_template=payload.code_template,
            code_test_cases=payload.code_test_cases or [],
            created_by=creator_id,
            verification_status="APPROVED",
            version=1,
        )
        db.add(question)
        db.flush()

        # 4. Handle Options for objective questions
        if payload.options:
            has_correct = False
            for opt_idx, opt_data in enumerate(payload.options):
                if opt_data.is_correct:
                    has_correct = True
                option = AssessmentQuestionOption(
                    question_id=question.id,
                    option_text=opt_data.option_text,
                    display_order=opt_data.display_order or (opt_idx + 1),
                    is_correct=opt_data.is_correct,
                    explanation=opt_data.explanation,
                )
                db.add(option)

            q_type = payload.question_type.value if hasattr(payload.question_type, 'value') else payload.question_type
            if q_type in [QuestionType.MCQ.value, QuestionType.TRUE_FALSE.value, QuestionType.MULTI_SELECT.value] and not has_correct:
                logger.warning("Objective question created without any option marked as correct.")

        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def get_questions(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None,
        learning_outcome_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AssessmentQuestion]:
        query = select(AssessmentQuestion).where(AssessmentQuestion.institution_id == institution_id)

        if subject_id:
            query = query.where(AssessmentQuestion.subject_id == subject_id)
        if difficulty:
            query = query.where(AssessmentQuestion.difficulty == difficulty)
        if question_type:
            query = query.where(AssessmentQuestion.question_type == question_type)
        if learning_outcome_id:
            query = query.where(AssessmentQuestion.learning_outcome_id == learning_outcome_id)
        if search:
            query = query.where(AssessmentQuestion.question_text.ilike(f"%{search}%"))

        query = query.order_by(AssessmentQuestion.created_at.desc()).offset(skip).limit(limit)
        return list(db.execute(query).scalars().all())

    @staticmethod
    def get_question_by_id(
        db: Session,
        institution_id: uuid.UUID,
        question_id: uuid.UUID,
    ) -> AssessmentQuestion:
        question = db.execute(
            select(AssessmentQuestion).where(
                AssessmentQuestion.id == question_id,
                AssessmentQuestion.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment question not found.",
            )
        return question

    @staticmethod
    def update_question(
        db: Session,
        institution_id: uuid.UUID,
        question_id: uuid.UUID,
        payload: QuestionUpdate,
    ) -> AssessmentQuestion:
        question = QuestionService.get_question_by_id(db, institution_id, question_id)

        if payload.question_text is not None:
            question.question_text = payload.question_text
        if payload.difficulty is not None:
            question.difficulty = payload.difficulty.value if hasattr(payload.difficulty, 'value') else payload.difficulty
        if payload.bloom_level is not None:
            question.bloom_level = payload.bloom_level
        if payload.default_marks is not None:
            question.default_marks = payload.default_marks
        if payload.explanation is not None:
            question.explanation = payload.explanation
        if payload.expected_answer is not None:
            question.expected_answer = payload.expected_answer
        if payload.evaluation_method is not None:
            question.evaluation_method = payload.evaluation_method.value if hasattr(payload.evaluation_method, 'value') else payload.evaluation_method
        if payload.verification_status is not None:
            question.verification_status = payload.verification_status
        if payload.unit_id is not None:
            question.unit_id = payload.unit_id
        if payload.topic_id is not None:
            question.topic_id = payload.topic_id
        if payload.learning_outcome_id is not None:
            question.learning_outcome_id = payload.learning_outcome_id
        if payload.competency_id is not None:
            question.competency_id = payload.competency_id

        # Update options if provided
        if payload.options is not None:
            # Delete existing options and insert updated ones
            for existing_opt in question.options:
                db.delete(existing_opt)
            db.flush()

            for opt_idx, opt_data in enumerate(payload.options):
                option = AssessmentQuestionOption(
                    question_id=question.id,
                    option_text=opt_data.option_text,
                    display_order=opt_data.display_order or (opt_idx + 1),
                    is_correct=opt_data.is_correct,
                    explanation=opt_data.explanation,
                )
                db.add(option)

        question.version += 1
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def generate_draft_questions_ai(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: uuid.UUID,
        topic_id: Optional[uuid.UUID] = None,
        learning_outcome_id: Optional[uuid.UUID] = None,
        count: int = 3,
    ) -> List[AssessmentQuestion]:
        """
        Generates draft questions mapped to approved curriculum nodes.
        Strictly tagged as DRAFT and requires faculty review.
        """
        subject = db.execute(
            select(AcademicSubject).where(
                AcademicSubject.id == subject_id,
                AcademicSubject.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found for draft question generation.",
            )

        # Retrieve topic and outcome context
        topic_name = "Core Subject Fundamentals"
        if topic_id:
            top = db.execute(select(SyllabusTopic).where(SyllabusTopic.id == topic_id)).scalar_one_or_none()
            if top:
                topic_name = top.topic_name

        outcome_desc = "Demonstrate comprehension and analytical reasoning."
        bloom = BloomTaxonomyLevel.APPLY.value
        if learning_outcome_id:
            lo = db.execute(select(LearningOutcome).where(LearningOutcome.id == learning_outcome_id)).scalar_one_or_none()
            if lo:
                outcome_desc = lo.description
                bloom = lo.bloom_level

        generated_questions: List[AssessmentQuestion] = []
        for i in range(count):
            q = AssessmentQuestion(
                institution_id=institution_id,
                subject_id=subject_id,
                topic_id=topic_id,
                learning_outcome_id=learning_outcome_id,
                question_text=f"AI Draft [{subject.code} - {topic_name}]: Explain the computational and architectural implications of {topic_name} in relation to {outcome_desc[:60]}... (Item {i+1})",
                question_type=QuestionType.SHORT_ANSWER.value if i % 2 == 1 else QuestionType.MCQ.value,
                difficulty=QuestionDifficulty.MEDIUM.value,
                bloom_level=bloom,
                default_marks=2.0 if i % 2 == 1 else 1.0,
                explanation=f"Generated draft question based on syllabus topic {topic_name}.",
                expected_answer=f"Synthesize key principles of {topic_name} and apply them to standard scenarios.",
                evaluation_method=QuestionEvaluationMethod.MANUAL.value if i % 2 == 1 else QuestionEvaluationMethod.AUTOMATIC.value,
                verification_status="DRAFT",
                version=1,
            )
            db.add(q)
            db.flush()

            if q.question_type == QuestionType.MCQ.value:
                db.add_all([
                    AssessmentQuestionOption(question_id=q.id, option_text=f"Primary optimal structure for {topic_name}", display_order=1, is_correct=True),
                    AssessmentQuestionOption(question_id=q.id, option_text=f"Secondary suboptimal configuration", display_order=2, is_correct=False),
                    AssessmentQuestionOption(question_id=q.id, option_text="Incompatible theoretical baseline", display_order=3, is_correct=False),
                    AssessmentQuestionOption(question_id=q.id, option_text="Undefined boundary case", display_order=4, is_correct=False),
                ])
            generated_questions.append(q)

        db.commit()
        for q in generated_questions:
            db.refresh(q)
        return generated_questions
