from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.security import (
    CurrentUser,
    get_current_active_user,
    require_roles,
    UserRole,
)
from app.db.session import get_db
from app.models.institution import Institution, InstitutionMembership
from app.models.profile import Profile
from app.schemas.auth import (
    InstitutionResponse,
    InstitutionMemberResponse,
    MemberStatusUpdate,
)

router = APIRouter(prefix="/institutions", tags=["Institution Management"])


@router.get("/me", response_model=Optional[InstitutionResponse], summary="Get Current User Institution")
def get_my_institution(
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[InstitutionResponse]:
    """Returns the current user's affiliated institution profile."""
    if not current_user.institution_id:
        return None

    if db:
        try:
            inst = db.query(Institution).filter(
                Institution.id == uuid.UUID(current_user.institution_id)
            ).first()
            if inst:
                return InstitutionResponse(
                    id=str(inst.id),
                    name=inst.name,
                    institution_code=inst.institution_code,
                    institution_type=inst.institution_type,
                    city=inst.city,
                    state=inst.state,
                    country=inst.country,
                    is_active=inst.is_active,
                    created_at=inst.created_at,
                )
        except Exception:
            pass

    return None


@router.get(
    "/{institution_id}/members",
    response_model=List[InstitutionMemberResponse],
    summary="Get Institution Membership Roster",
)
def get_institution_members(
    institution_id: str,
    current_user: CurrentUser = Depends(
        require_roles(UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: Session = Depends(get_db),
) -> List[InstitutionMemberResponse]:
    """
    Roster of institution members.
    Enforces that INSTITUTION_ADMIN can only view their own institution.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.institution_id != str(institution_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access membership records for your designated institution.",
            )

    results: List[InstitutionMemberResponse] = []
    if db:
        try:
            memberships = (
                db.query(InstitutionMembership)
                .join(Profile, Profile.id == InstitutionMembership.user_id)
                .filter(InstitutionMembership.institution_id == uuid.UUID(institution_id))
                .all()
            )
            for m in memberships:
                results.append(
                    InstitutionMemberResponse(
                        id=str(m.id),
                        institution_id=str(m.institution_id),
                        user_id=str(m.user_id),
                        full_name=m.profile.full_name if m.profile else "Unknown",
                        email=m.profile.email if m.profile else "",
                        membership_role=m.membership_role,
                        membership_status=m.membership_status,
                        created_at=m.created_at,
                    )
                )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query error: {str(exc)}",
            )

    return results


@router.patch(
    "/{institution_id}/members/{user_id}",
    response_model=InstitutionMemberResponse,
    summary="Update Institution Member Status or Role",
)
def update_member_status(
    institution_id: str,
    user_id: str,
    payload: MemberStatusUpdate,
    current_user: CurrentUser = Depends(
        require_roles(UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: Session = Depends(get_db),
) -> InstitutionMemberResponse:
    """
    Allows authorized administrators to approve, suspend, or update member status.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.institution_id != str(institution_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot administer members outside your institution.",
            )

    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available for membership status updates.",
        )

    try:
        membership = (
            db.query(InstitutionMembership)
            .filter(
                InstitutionMembership.institution_id == uuid.UUID(institution_id),
                InstitutionMembership.user_id == uuid.UUID(user_id),
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution membership record not found.",
            )

        membership.membership_status = payload.membership_status.value
        if payload.membership_role:
            membership.membership_role = payload.membership_role.value

        # Synchronize account_status on the profile if status is changed
        profile = db.query(Profile).filter(Profile.id == uuid.UUID(user_id)).first()
        if profile:
            profile.account_status = payload.membership_status.value

        db.commit()
        db.refresh(membership)

        return InstitutionMemberResponse(
            id=str(membership.id),
            institution_id=str(membership.institution_id),
            user_id=str(membership.user_id),
            full_name=profile.full_name if profile else "Unknown",
            email=profile.email if profile else "",
            membership_role=membership.membership_role,
            membership_status=membership.membership_status,
            created_at=membership.created_at,
        )
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member status: {str(exc)}",
        )
