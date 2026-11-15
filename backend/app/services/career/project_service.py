import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.career import (
    StudentProjectEvidence,
    StudentCompetencyEvidence,
)
from app.models.academic_data import StudentAcademicProfile
from app.models.enums import (
    ProjectVerificationStatus,
    CompetencyEvidenceState,
    CompetencyEvidenceType,
)
from app.schemas.career import (
    StudentProjectEvidenceCreate,
    StudentProjectEvidenceUpdate,
    StudentProjectEvidenceReview,
)


class ProjectEvidenceService:
    @staticmethod
    def get_student_profile_id(db: Session, user_id: uuid.UUID) -> uuid.UUID:
        profile = db.query(StudentAcademicProfile).filter(
            StudentAcademicProfile.profile_id == user_id
        ).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student academic profile not found for this user account.",
            )
        return profile.id

    @staticmethod
    def list_student_projects(
        db: Session,
        student_id: uuid.UUID,
        institution_id: Optional[uuid.UUID] = None,
    ) -> List[StudentProjectEvidence]:
        query = db.query(StudentProjectEvidence).filter(
            StudentProjectEvidence.student_id == student_id
        )
        if institution_id:
            query = query.filter(StudentProjectEvidence.institution_id == institution_id)
        return query.order_by(StudentProjectEvidence.created_at.desc()).all()

    @staticmethod
    def list_pending_verification_projects(
        db: Session,
        institution_id: uuid.UUID,
    ) -> List[StudentProjectEvidence]:
        return db.query(StudentProjectEvidence).filter(
            StudentProjectEvidence.institution_id == institution_id,
            StudentProjectEvidence.verification_status == ProjectVerificationStatus.PENDING_REVIEW.value,
        ).order_by(StudentProjectEvidence.created_at.desc()).all()

    @staticmethod
    def get_project_by_id(db: Session, project_id: uuid.UUID) -> StudentProjectEvidence:
        project = db.query(StudentProjectEvidence).filter(
            StudentProjectEvidence.id == project_id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project evidence '{project_id}' not found.",
            )
        return project

    @staticmethod
    def submit_project(
        db: Session,
        project_in: StudentProjectEvidenceCreate,
        student_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> StudentProjectEvidence:
        project = StudentProjectEvidence(
            institution_id=institution_id,
            student_id=student_id,
            title=project_in.title,
            description=project_in.description,
            technology_stack=project_in.technology_stack,
            repository_url=project_in.repository_url,
            portfolio_url=project_in.portfolio_url,
            documentation_url=project_in.documentation_url,
            demonstrated_competencies=project_in.demonstrated_competencies,
            verification_status=ProjectVerificationStatus.PENDING_REVIEW.value,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: uuid.UUID,
        project_in: StudentProjectEvidenceUpdate,
        student_id: uuid.UUID,
    ) -> StudentProjectEvidence:
        project = ProjectEvidenceService.get_project_by_id(db, project_id)
        if project.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own project evidence.",
            )
        if project.verification_status == ProjectVerificationStatus.VERIFIED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verified project evidence cannot be modified. Submit a new revision or consult faculty.",
            )
        
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def review_project(
        db: Session,
        project_id: uuid.UUID,
        review_in: StudentProjectEvidenceReview,
        reviewer_id: uuid.UUID,
    ) -> StudentProjectEvidence:
        project = ProjectEvidenceService.get_project_by_id(db, project_id)
        project.verification_status = review_in.verification_status.value
        project.verification_notes = review_in.verification_notes
        project.reviewer_id = reviewer_id
        project.reviewed_at = datetime.now()

        # If VERIFIED, register/update competency evidence entries
        if review_in.verification_status == ProjectVerificationStatus.VERIFIED:
            for comp_name in project.demonstrated_competencies:
                existing = db.query(StudentCompetencyEvidence).filter(
                    StudentCompetencyEvidence.student_id == project.student_id,
                    StudentCompetencyEvidence.competency_name == comp_name,
                    StudentCompetencyEvidence.source_entity_id == project.id,
                ).first()

                if not existing:
                    evidence = StudentCompetencyEvidence(
                        institution_id=project.institution_id,
                        student_id=project.student_id,
                        competency_name=comp_name,
                        category="PRACTICAL",
                        evidence_type=CompetencyEvidenceType.PROJECT_DEMONSTRATION.value,
                        source_entity_type="STUDENT_PROJECT_EVIDENCE",
                        source_entity_id=project.id,
                        evidence_state=CompetencyEvidenceState.DEMONSTRATED.value,
                        score_or_metric=90.0,
                        evidence_summary=f"Verified project: '{project.title}' using {', '.join(project.technology_stack)}.",
                        provenance_details={
                            "project_title": project.title,
                            "repository_url": project.repository_url,
                            "reviewer_id": str(reviewer_id),
                        },
                        verified_by=reviewer_id,
                        verified_at=datetime.now(),
                        is_eligible=True,
                    )
                    db.add(evidence)

        db.commit()
        db.refresh(project)
        return project
