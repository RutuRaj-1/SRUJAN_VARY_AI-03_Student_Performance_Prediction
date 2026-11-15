import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.enums import DocumentStatus, ReviewStatus
from app.models.syllabus import (
    SyllabusDocument,
    SyllabusUnit,
    SyllabusTopic,
    Competency,
    SyllabusReviewHistory,
)
from app.models.profile import Profile
from app.schemas.syllabus import (
    UnitUpdateRequest,
    TopicUpdateRequest,
    SyllabusReviewHistoryResponse,
)


class SyllabusReviewService:
    def review_document(
        self,
        db: Session,
        document_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        action: str,  # "APPROVED", "REJECTED"
        comments: Optional[str] = None,
    ) -> SyllabusDocument:
        doc = db.get(SyllabusDocument, document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Syllabus document not found.")

        prev_status = doc.status
        action_upper = action.strip().upper()

        if action_upper == "APPROVED":
            new_status = DocumentStatus.APPROVED.value
            # Mark all competencies linked to this document/subject as verified
            if doc.subject_id:
                competencies = (
                    db.query(Competency)
                    .filter(Competency.institution_id == doc.institution_id)
                    .all()
                )
                for comp in competencies:
                    comp.is_verified = True
        elif action_upper == "REJECTED":
            new_status = DocumentStatus.REJECTED.value
        else:
            new_status = DocumentStatus.REVIEW_REQUIRED.value

        doc.status = new_status

        # Record audit history
        audit = SyllabusReviewHistory(
            id=uuid.uuid4(),
            document_id=doc.id,
            reviewed_by=reviewer_id,
            action=action_upper,
            entity_type="DOCUMENT",
            entity_id=doc.id,
            previous_value={"status": prev_status},
            new_value={"status": new_status},
            comments=comments,
        )
        db.add(audit)
        db.commit()
        db.refresh(doc)
        return doc

    def update_unit(
        self,
        db: Session,
        unit_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        update_data: UnitUpdateRequest,
        comments: Optional[str] = None,
    ) -> SyllabusUnit:
        unit = db.get(SyllabusUnit, unit_id)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found.")

        prev_val = {
            "title": unit.title,
            "estimated_hours": unit.estimated_hours,
            "description": unit.description,
        }

        if update_data.title is not None:
            unit.title = update_data.title
        if update_data.estimated_hours is not None:
            unit.estimated_hours = update_data.estimated_hours
        if update_data.description is not None:
            unit.description = update_data.description

        new_val = {
            "title": unit.title,
            "estimated_hours": unit.estimated_hours,
            "description": unit.description,
        }

        audit = SyllabusReviewHistory(
            id=uuid.uuid4(),
            document_id=unit.document_id,
            reviewed_by=reviewer_id,
            action="UNIT_UPDATED",
            entity_type="UNIT",
            entity_id=unit.id,
            previous_value=prev_val,
            new_value=new_val,
            comments=comments,
        )
        db.add(audit)
        db.commit()
        db.refresh(unit)
        return unit

    def update_topic(
        self,
        db: Session,
        topic_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        update_data: TopicUpdateRequest,
        comments: Optional[str] = None,
    ) -> SyllabusTopic:
        topic = db.get(SyllabusTopic, topic_id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found.")

        prev_val = {
            "topic_name": topic.topic_name,
            "subtopics": topic.subtopics,
        }

        if update_data.topic_name is not None:
            topic.topic_name = update_data.topic_name
        if update_data.subtopics is not None:
            topic.subtopics = update_data.subtopics

        new_val = {
            "topic_name": topic.topic_name,
            "subtopics": topic.subtopics,
        }

        audit = SyllabusReviewHistory(
            id=uuid.uuid4(),
            document_id=topic.unit.document_id,
            reviewed_by=reviewer_id,
            action="TOPIC_UPDATED",
            entity_type="TOPIC",
            entity_id=topic.id,
            previous_value=prev_val,
            new_value=new_val,
            comments=comments,
        )
        db.add(audit)
        db.commit()
        db.refresh(topic)
        return topic

    def get_review_history(
        self,
        db: Session,
        document_id: uuid.UUID,
    ) -> List[SyllabusReviewHistoryResponse]:
        stmt = (
            select(SyllabusReviewHistory, Profile)
            .outerjoin(Profile, SyllabusReviewHistory.reviewed_by == Profile.id)
            .where(SyllabusReviewHistory.document_id == document_id)
            .order_by(SyllabusReviewHistory.created_at.desc())
        )
        results = db.execute(stmt).all()
        history = []
        for audit, profile in results:
            history.append(
                SyllabusReviewHistoryResponse(
                    id=audit.id,
                    document_id=audit.document_id,
                    reviewed_by=audit.reviewed_by,
                    reviewer_name=profile.full_name if profile else "System",
                    action=audit.action,
                    entity_type=audit.entity_type,
                    entity_id=audit.entity_id,
                    previous_value=audit.previous_value,
                    new_value=audit.new_value,
                    comments=audit.comments,
                    created_at=audit.created_at,
                )
            )
        return history


review_service = SyllabusReviewService()
