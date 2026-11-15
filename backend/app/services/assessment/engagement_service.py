import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.models.assessment import (
    LearningEngagementEvent,
    AssessmentAttempt,
)
from app.models.academic_data import AcademicAssessment
from app.models.enums import LearningEngagementEventType
from app.schemas.assessment import LearningEngagementSummary
from app.core.logging import logger


class EngagementService:
    @staticmethod
    def record_event(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        assessment_id: uuid.UUID,
        attempt_id: Optional[uuid.UUID],
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "WEB",
    ) -> LearningEngagementEvent:
        """
        Records a transparent observable interaction event.
        Strictly excludes invasive biometric, keystroke, or video telemetry.
        """
        # Sanitize metadata to avoid capturing sensitive or PII data
        sanitized_metadata = metadata or {}
        if "password" in sanitized_metadata:
            sanitized_metadata.pop("password", None)

        event = LearningEngagementEvent(
            institution_id=institution_id,
            student_id=student_id,
            assessment_id=assessment_id,
            attempt_id=attempt_id,
            event_type=event_type,
            event_timestamp=datetime.now(timezone.utc),
            event_metadata=sanitized_metadata,
            source=source,
        )
        db.add(event)
        # We do not necessarily commit here to allow embedding inside parent transactions
        db.flush()
        return event

    @staticmethod
    def get_attempt_engagement(
        db: Session,
        institution_id: uuid.UUID,
        attempt_id: uuid.UUID,
    ) -> List[LearningEngagementEvent]:
        return list(
            db.execute(
                select(LearningEngagementEvent)
                .where(
                    LearningEngagementEvent.attempt_id == attempt_id,
                    LearningEngagementEvent.institution_id == institution_id,
                )
                .order_by(LearningEngagementEvent.event_timestamp.asc())
            ).scalars().all()
        )

    @staticmethod
    def get_assessment_engagement_summary(
        db: Session,
        institution_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> LearningEngagementSummary:
        # Total events for this assessment
        total_events = db.execute(
            select(func.count(LearningEngagementEvent.id)).where(
                LearningEngagementEvent.assessment_id == assessment_id,
                LearningEngagementEvent.institution_id == institution_id,
            )
        ).scalar() or 0

        # Attempt statistics
        total_attempts = db.execute(
            select(func.count(AssessmentAttempt.id)).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar() or 0

        completed_attempts = db.execute(
            select(func.count(AssessmentAttempt.id)).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.institution_id == institution_id,
                AssessmentAttempt.attempt_status.in_(["SUBMITTED", "EVALUATED"]),
            )
        ).scalar() or 0

        in_progress_attempts = db.execute(
            select(func.count(AssessmentAttempt.id)).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.institution_id == institution_id,
                AssessmentAttempt.attempt_status == "IN_PROGRESS",
            )
        ).scalar() or 0

        # Revision events count
        total_revisions = db.execute(
            select(func.count(LearningEngagementEvent.id)).where(
                LearningEngagementEvent.assessment_id == assessment_id,
                LearningEngagementEvent.institution_id == institution_id,
                LearningEngagementEvent.event_type == LearningEngagementEventType.ANSWER_REVISED.value,
            )
        ).scalar() or 0

        # Unique participating students
        unique_students = db.execute(
            select(func.count(func.distinct(AssessmentAttempt.student_id))).where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.institution_id == institution_id,
            )
        ).scalar() or 0

        # Enrolled students count for participation rate
        asmt = db.execute(
            select(AcademicAssessment).where(
                AcademicAssessment.id == assessment_id,
                AcademicAssessment.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        participation_rate = 0.0
        if asmt:
            from app.models.academic_data import StudentSubjectEnrollment
            enrolled_count = db.execute(
                select(func.count(StudentSubjectEnrollment.id)).where(
                    StudentSubjectEnrollment.subject_id == asmt.subject_id,
                    StudentSubjectEnrollment.institution_id == institution_id,
                    StudentSubjectEnrollment.enrollment_status == "ACTIVE",
                )
            ).scalar() or 0
            if enrolled_count > 0:
                participation_rate = round((unique_students / enrolled_count) * 100.0, 1)

        avg_rev = round(total_revisions / total_attempts, 2) if total_attempts > 0 else 0.0

        return LearningEngagementSummary(
            total_events=total_events,
            participation_rate=participation_rate,
            total_attempts=total_attempts,
            completed_attempts=completed_attempts,
            in_progress_attempts=in_progress_attempts,
            average_revision_count=avg_rev,
            total_answer_revisions=total_revisions,
        )
