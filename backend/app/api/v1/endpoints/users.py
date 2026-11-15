from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.models.profile import Profile
from app.schemas.auth import UserMeResponse, ProfileUpdate

router = APIRouter(prefix="/users", tags=["User Profile Management"])


@router.get("/me", response_model=UserMeResponse, summary="Get Current User Profile")
def get_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
) -> UserMeResponse:
    """Returns the current user profile."""
    return UserMeResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        account_status=current_user.account_status,
        institution_id=current_user.institution_id,
        permissions=list(current_user.permissions),
    )


@router.patch("/me", response_model=UserMeResponse, summary="Update Self-Editable Profile Fields")
def update_user_profile(
    update_data: ProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserMeResponse:
    """
    Allows updating only explicitly permitted self-editable profile fields:
    full_name, phone, avatar_url.
    Modifying role, account_status, or institution_id through this endpoint is strictly disallowed.
    """
    updated_name = current_user.full_name
    if db:
        try:
            profile = db.query(Profile).filter(Profile.id == uuid.UUID(current_user.user_id)).first()
            if profile:
                if update_data.full_name is not None:
                    profile.full_name = update_data.full_name.strip()
                    updated_name = profile.full_name
                if update_data.phone is not None:
                    profile.phone = update_data.phone.strip()
                if update_data.avatar_url is not None:
                    profile.avatar_url = update_data.avatar_url.strip()
                db.commit()
                db.refresh(profile)
        except Exception as exc:
            if db:
                db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update profile: {str(exc)}",
            )
    else:
        if update_data.full_name:
            updated_name = update_data.full_name.strip()

    return UserMeResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=updated_name,
        role=current_user.role,
        account_status=current_user.account_status,
        institution_id=current_user.institution_id,
        permissions=list(current_user.permissions),
    )
