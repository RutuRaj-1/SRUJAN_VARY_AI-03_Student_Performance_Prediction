import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.career import CareerDevelopmentRecommendation
from app.models.enums import CareerRecommendationStatus
from app.schemas.career import (
    CareerDevelopmentRecommendationCreate,
    CareerDevelopmentRecommendationUpdate,
)


class CareerRecommendationService:
    @staticmethod
    def list_student_recommendations(
        db: Session,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
        role_id: Optional[uuid.UUID] = None,
    ) -> List[CareerDevelopmentRecommendation]:
        query = db.query(CareerDevelopmentRecommendation).filter(
            CareerDevelopmentRecommendation.student_id == student_id,
            CareerDevelopmentRecommendation.institution_id == institution_id,
        )
        if role_id:
            query = query.filter(CareerDevelopmentRecommendation.role_id == role_id)
        return query.order_by(CareerDevelopmentRecommendation.created_at.desc()).all()

    @staticmethod
    def get_recommendation_by_id(
        db: Session,
        recommendation_id: uuid.UUID,
    ) -> CareerDevelopmentRecommendation:
        rec = db.query(CareerDevelopmentRecommendation).filter(
            CareerDevelopmentRecommendation.id == recommendation_id
        ).first()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Career development recommendation '{recommendation_id}' not found.",
            )
        return rec

    @staticmethod
    def update_recommendation(
        db: Session,
        recommendation_id: uuid.UUID,
        rec_in: CareerDevelopmentRecommendationUpdate,
        user_id: uuid.UUID,
        is_staff: bool = False,
    ) -> CareerDevelopmentRecommendation:
        rec = CareerRecommendationService.get_recommendation_by_id(db, recommendation_id)
        
        if rec_in.status:
            rec.status = rec_in.status
        if rec_in.student_notes:
            rec.student_notes = rec_in.student_notes
        if is_staff and rec_in.reviewer_feedback:
            rec.reviewer_feedback = rec_in.reviewer_feedback

        db.commit()
        db.refresh(rec)
        return rec
