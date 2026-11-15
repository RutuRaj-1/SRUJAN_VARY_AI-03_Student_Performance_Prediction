import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.interventions import InterventionTemplate
from app.models.enums import InterventionType
from app.schemas.interventions import InterventionTemplateCreate, InterventionTemplateUpdate
from app.core.logging import logger

DEFAULT_TEMPLATES_SEED = [
    {
        "template_code": "TPL_TOPIC_REVISION",
        "template_name": "Targeted Topic Conceptual Revision",
        "intervention_type": InterventionType.TARGETED_REVISION.value,
        "description": "Guided conceptual review addressing specific syllabus topic weaknesses identified through continuous assessments.",
        "target_level": "TOPIC",
        "suggested_duration_hours": 3.0,
        "suggested_completion_days": 7,
        "recommended_actions_template": [
            {"order": 1, "title": "Review Topic Reading Material & Key Concept Notes", "type": "TARGETED_REVISION", "hours": 1.5},
            {"order": 2, "title": "Complete 3 Guided Practice Problems with Self-Check", "type": "PRACTICE_SET", "hours": 1.5},
        ],
        "required_resources": [{"title": "Course Textbook & Faculty Lecture Slides", "type": "READING"}],
        "expected_evidence_type": "STUDENT_NOTES_OR_SOLUTIONS",
        "requires_faculty_review": True,
    },
    {
        "template_code": "TPL_PRACTICE_SET",
        "template_name": "Adaptive Problem Practice Set",
        "intervention_type": InterventionType.PRACTICE_SET.value,
        "description": "Targeted problem set focusing on low-attainment Bloom's taxonomy cognitive levels (Apply / Analyze).",
        "target_level": "TOPIC",
        "suggested_duration_hours": 2.5,
        "suggested_completion_days": 5,
        "recommended_actions_template": [
            {"order": 1, "title": "Attempt Practice Problem Set Part A (Foundational)", "type": "PRACTICE_SET", "hours": 1.0},
            {"order": 2, "title": "Attempt Practice Problem Set Part B (Applied)", "type": "PRACTICE_SET", "hours": 1.5},
        ],
        "required_resources": [{"title": "Practice Question Bank Repository", "type": "QUESTION_BANK"}],
        "expected_evidence_type": "ASSIGNMENT_SUBMISSION",
        "requires_faculty_review": True,
    },
    {
        "template_code": "TPL_DIAGNOSTIC_EVAL",
        "template_name": "Formative Diagnostic & Evidence Gathering",
        "intervention_type": InterventionType.FORMATIVE_ASSESSMENT.value,
        "description": "Low-stakes formative diagnostic assessment designed to establish baseline understanding for unassessed or insufficient evidence topics.",
        "target_level": "TOPIC",
        "suggested_duration_hours": 1.0,
        "suggested_completion_days": 4,
        "recommended_actions_template": [
            {"order": 1, "title": "Complete Low-Stakes 10-Question Formative Probe", "type": "FORMATIVE_ASSESSMENT", "hours": 1.0},
        ],
        "required_resources": [{"title": "Low-Stakes Diagnostic Quiz Form", "type": "QUIZ"}],
        "expected_evidence_type": "FORMATIVE_ATTEMPT",
        "requires_faculty_review": False,
    },
    {
        "template_code": "TPL_FACULTY_OFFICE_HOURS",
        "template_name": "1-on-1 Faculty Advisory Consultation",
        "intervention_type": InterventionType.FACULTY_CONSULTATION.value,
        "description": "Direct pedagogical advising session to clarify prerequisite misunderstandings and co-design a recovery study plan.",
        "target_level": "SUBJECT",
        "suggested_duration_hours": 1.0,
        "suggested_completion_days": 7,
        "recommended_actions_template": [
            {"order": 1, "title": "Prepare 3 Specific Topic Questions for Office Hours", "type": "FACULTY_CONSULTATION", "hours": 0.5},
            {"order": 2, "title": "Attend Faculty Consultation Session", "type": "FACULTY_CONSULTATION", "hours": 0.5},
        ],
        "required_resources": [{"title": "Faculty Office Hours Schedule", "type": "CALENDAR"}],
        "expected_evidence_type": "CONSULTATION_LOG",
        "requires_faculty_review": True,
    },
]


class InterventionTemplateService:
    @staticmethod
    def seed_default_templates_if_empty(db: Session, institution_id: uuid.UUID) -> List[InterventionTemplate]:
        """
        Seeds standard institutional intervention templates if none exist for the tenant.
        """
        existing = (
            db.query(InterventionTemplate)
            .filter(InterventionTemplate.institution_id == institution_id)
            .all()
        )
        if existing:
            return existing

        created_templates = []
        for seed in DEFAULT_TEMPLATES_SEED:
            tpl = InterventionTemplate(
                id=uuid.uuid4(),
                institution_id=institution_id,
                template_code=seed["template_code"],
                template_name=seed["template_name"],
                intervention_type=seed["intervention_type"],
                description=seed["description"],
                target_level=seed["target_level"],
                suggested_duration_hours=seed["suggested_duration_hours"],
                suggested_completion_days=seed["suggested_completion_days"],
                recommended_actions_template=seed["recommended_actions_template"],
                required_resources=seed["required_resources"],
                expected_evidence_type=seed["expected_evidence_type"],
                requires_faculty_review=seed["requires_faculty_review"],
                is_active=True,
            )
            db.add(tpl)
            created_templates.append(tpl)

        db.commit()
        for t in created_templates:
            db.refresh(t)
        logger.info(f"Seeded {len(created_templates)} default intervention templates for institution {institution_id}")
        return created_templates

    @staticmethod
    def get_templates(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
        intervention_type: Optional[str] = None,
        active_only: bool = True,
    ) -> List[InterventionTemplate]:
        InterventionTemplateService.seed_default_templates_if_empty(db, institution_id)
        query = db.query(InterventionTemplate).filter(InterventionTemplate.institution_id == institution_id)

        if active_only:
            query = query.filter(InterventionTemplate.is_active.is_(True))

        if subject_id:
            query = query.filter(
                (InterventionTemplate.subject_id == subject_id) | (InterventionTemplate.subject_id.is_(None))
            )

        if intervention_type:
            query = query.filter(InterventionTemplate.intervention_type == intervention_type)

        return query.order_by(InterventionTemplate.template_name).all()

    @staticmethod
    def get_template_by_id(
        db: Session,
        template_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> Optional[InterventionTemplate]:
        return (
            db.query(InterventionTemplate)
            .filter(
                InterventionTemplate.id == template_id,
                InterventionTemplate.institution_id == institution_id,
            )
            .first()
        )

    @staticmethod
    def create_template(
        db: Session,
        institution_id: uuid.UUID,
        payload: InterventionTemplateCreate,
        creator_id: Optional[uuid.UUID] = None,
    ) -> InterventionTemplate:
        tpl = InterventionTemplate(
            id=uuid.uuid4(),
            institution_id=institution_id,
            subject_id=payload.subject_id,
            template_code=payload.template_code,
            template_name=payload.template_name,
            intervention_type=payload.intervention_type.value,
            description=payload.description,
            target_level=payload.target_level,
            suggested_duration_hours=payload.suggested_duration_hours,
            suggested_completion_days=payload.suggested_completion_days,
            recommended_actions_template=payload.recommended_actions_template,
            required_resources=payload.required_resources,
            expected_evidence_type=payload.expected_evidence_type,
            requires_faculty_review=payload.requires_faculty_review,
            is_active=payload.is_active,
            created_by_profile_id=creator_id,
        )
        db.add(tpl)
        db.commit()
        db.refresh(tpl)
        logger.info(f"Created intervention template '{tpl.template_name}' ({tpl.id})")
        return tpl


intervention_template_service = InterventionTemplateService()
