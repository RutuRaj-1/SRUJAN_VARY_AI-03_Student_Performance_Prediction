import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.risk import AcademicRiskTarget
from app.models.enums import RiskTargetStatus
from app.schemas.risk import RiskTargetCreateRequest, RiskTargetUpdateRequest
from app.core.logging import logger


class RiskTargetService:
    """
    Manages institutional academic outcome target definitions and thresholds.
    """

    @staticmethod
    def get_targets(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: Optional[uuid.UUID] = None,
    ) -> List[AcademicRiskTarget]:
        query = db.query(AcademicRiskTarget).filter(AcademicRiskTarget.institution_id == institution_id)
        if subject_id:
            query = query.filter(
                (AcademicRiskTarget.subject_id == subject_id) | (AcademicRiskTarget.subject_id.is_(None))
            )
        return query.order_by(AcademicRiskTarget.created_at.desc()).all()

    @staticmethod
    def get_target_by_id(
        db: Session,
        target_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> AcademicRiskTarget:
        target = (
            db.query(AcademicRiskTarget)
            .filter(
                AcademicRiskTarget.id == target_id,
                AcademicRiskTarget.institution_id == institution_id,
            )
            .first()
        )
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Academic risk target {target_id} not found in this institution.",
            )
        return target

    @staticmethod
    def create_target(
        db: Session,
        institution_id: uuid.UUID,
        req: RiskTargetCreateRequest,
    ) -> AcademicRiskTarget:
        # Check uniqueness constraint
        existing = (
            db.query(AcademicRiskTarget)
            .filter(
                AcademicRiskTarget.institution_id == institution_id,
                AcademicRiskTarget.target_code == req.target_code,
                AcademicRiskTarget.subject_id == req.subject_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target with code '{req.target_code}' already exists for this scope.",
            )

        target = AcademicRiskTarget(
            institution_id=institution_id,
            subject_id=req.subject_id,
            target_code=req.target_code,
            target_name=req.target_name,
            description=req.description,
            academic_period=req.academic_period,
            outcome_definition=req.outcome_definition,
            positive_label_definition=req.positive_label_definition,
            negative_label_definition=req.negative_label_definition,
            passing_threshold_percentage=req.passing_threshold_percentage,
            prediction_horizon_weeks=req.prediction_horizon_weeks,
            status=RiskTargetStatus.ACTIVE.value,
            is_institution_policy=req.is_institution_policy,
        )
        db.add(target)
        db.commit()
        db.refresh(target)
        logger.info(f"Created academic risk target {target.id} ({target.target_code})")
        return target

    @staticmethod
    def update_target(
        db: Session,
        target_id: uuid.UUID,
        institution_id: uuid.UUID,
        req: RiskTargetUpdateRequest,
    ) -> AcademicRiskTarget:
        target = RiskTargetService.get_target_by_id(db, target_id, institution_id)

        if req.target_name is not None:
            target.target_name = req.target_name
        if req.description is not None:
            target.description = req.description
        if req.passing_threshold_percentage is not None:
            target.passing_threshold_percentage = req.passing_threshold_percentage
        if req.prediction_horizon_weeks is not None:
            target.prediction_horizon_weeks = req.prediction_horizon_weeks
        if req.status is not None:
            target.status = req.status.value
        if req.is_institution_policy is not None:
            target.is_institution_policy = req.is_institution_policy

        db.commit()
        db.refresh(target)
        return target

    @staticmethod
    def get_or_create_default_target(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> AcademicRiskTarget:
        target = (
            db.query(AcademicRiskTarget)
            .filter(
                AcademicRiskTarget.institution_id == institution_id,
                AcademicRiskTarget.subject_id == subject_id,
                AcademicRiskTarget.target_code == "COURSE_FAILURE_DEFICIT",
            )
            .first()
        )
        if not target:
            # Also check institution-wide target
            target = (
                db.query(AcademicRiskTarget)
                .filter(
                    AcademicRiskTarget.institution_id == institution_id,
                    AcademicRiskTarget.subject_id.is_(None),
                    AcademicRiskTarget.target_code == "COURSE_FAILURE_DEFICIT",
                )
                .first()
            )

        if not target:
            target = AcademicRiskTarget(
                institution_id=institution_id,
                subject_id=subject_id,
                target_code="COURSE_FAILURE_DEFICIT",
                target_name="Course Final Grade Deficit (<50%)",
                description="Final course aggregate performance below institutional threshold (50.0%).",
                academic_period="SEMESTER_FINAL",
                outcome_definition="Student scores below 50.0% in final verified course evaluations.",
                positive_label_definition="Final score < 50.0% (Risk Positive: in need of academic support)",
                negative_label_definition="Final score >= 50.0% (Risk Negative: demonstrated passing performance)",
                passing_threshold_percentage=50.0,
                prediction_horizon_weeks=4,
                status=RiskTargetStatus.ACTIVE.value,
                is_institution_policy=True,
            )
            db.add(target)
            db.commit()
            db.refresh(target)
        return target


risk_target_service = RiskTargetService()
