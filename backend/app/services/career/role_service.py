import uuid
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.syllabus import IndustryRoleProfile, IndustryCompetencyRequirement
from app.models.enums import RoleMappingStatus, IndustryImportance
from app.schemas.career import (
    IndustryRoleProfileCreate,
    IndustryRoleProfileUpdate,
    IndustryCompetencyRequirementCreate,
)


class RoleProfileService:
    @staticmethod
    def list_roles(
        db: Session,
        institution_id: Optional[uuid.UUID] = None,
        include_inactive: bool = False,
    ) -> List[IndustryRoleProfile]:
        """
        List permitted career role profiles (both global platform roles and institution-specific roles).
        """
        query = db.query(IndustryRoleProfile).options(
            joinedload(IndustryRoleProfile.requirements)
        )
        if not include_inactive:
            query = query.filter(IndustryRoleProfile.is_active == True)
        
        if institution_id:
            # Return global (institution_id IS NULL) + tenant-specific
            query = query.filter(
                (IndustryRoleProfile.institution_id == None) | 
                (IndustryRoleProfile.institution_id == institution_id)
            )
        else:
            # Global roles only
            query = query.filter(IndustryRoleProfile.institution_id == None)

        return query.order_by(IndustryRoleProfile.role_title).all()

    @staticmethod
    def get_role_by_id(db: Session, role_id: uuid.UUID) -> IndustryRoleProfile:
        role = db.query(IndustryRoleProfile).options(
            joinedload(IndustryRoleProfile.requirements)
        ).filter(IndustryRoleProfile.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Career role profile '{role_id}' not found.",
            )
        return role

    @staticmethod
    def create_role(
        db: Session,
        role_in: IndustryRoleProfileCreate,
        institution_id: Optional[uuid.UUID] = None,
    ) -> IndustryRoleProfile:
        role = IndustryRoleProfile(
            institution_id=institution_id or role_in.institution_id,
            role_title=role_in.role_title,
            role_family=role_in.role_family,
            description=role_in.description,
            experience_tier=role_in.experience_tier,
            version=role_in.version,
            is_active=role_in.is_active,
            review_status=role_in.review_status,
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def update_role(
        db: Session,
        role_id: uuid.UUID,
        role_in: IndustryRoleProfileUpdate,
    ) -> IndustryRoleProfile:
        role = RoleProfileService.get_role_by_id(db, role_id)
        update_data = role_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def add_requirement(
        db: Session,
        req_in: IndustryCompetencyRequirementCreate,
    ) -> IndustryCompetencyRequirement:
        role = RoleProfileService.get_role_by_id(db, req_in.role_id)
        req = IndustryCompetencyRequirement(
            role_id=role.id,
            competency_name=req_in.competency_name,
            category=req_in.category,
            required_depth=req_in.required_depth,
            importance=req_in.importance,
            description=req_in.description,
            competency_id=req_in.competency_id,
            mapping_status=req_in.mapping_status,
            source_reference=req_in.source_reference,
            rationale=req_in.rationale,
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req
