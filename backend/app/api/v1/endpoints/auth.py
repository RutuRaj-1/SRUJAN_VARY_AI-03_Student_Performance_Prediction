from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.security import (
    CurrentUser,
    get_current_user,
    get_current_active_user,
    get_permissions_for_role,
)
from app.db.session import get_db
from app.models.profile import Profile
from app.schemas.auth import UserMeResponse, PermissionsResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


@router.get("/me", response_model=UserMeResponse, summary="Get Current Authenticated User")
def get_auth_me(
    current_user: CurrentUser = Depends(get_current_user),
) -> UserMeResponse:
    """Returns the authenticated user's authoritative profile, role, status, and permissions."""
    return UserMeResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        account_status=current_user.account_status,
        institution_id=current_user.institution_id,
        permissions=list(current_user.permissions),
    )


@router.post("/refresh-profile", response_model=UserMeResponse, summary="Refresh Authoritative Profile")
def refresh_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserMeResponse:
    """
    Refreshes profile from the authoritative database source without
    trusting user-supplied roles or client-side metadata.
    """
    if db:
        try:
            profile = db.query(Profile).filter(Profile.id == uuid.UUID(current_user.user_id)).first()
            if profile:
                return UserMeResponse(
                    user_id=str(profile.id),
                    email=profile.email,
                    full_name=profile.full_name,
                    role=profile.role,
                    account_status=profile.account_status,
                    institution_id=str(profile.institution_id) if profile.institution_id else None,
                    permissions=list(get_permissions_for_role(profile.role)),
                )
        except Exception:
            pass

    return UserMeResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        account_status=current_user.account_status,
        institution_id=current_user.institution_id,
        permissions=list(current_user.permissions),
    )


@router.get("/permissions", response_model=PermissionsResponse, summary="Get Effective Permissions")
def get_user_permissions(
    current_user: CurrentUser = Depends(get_current_user),
) -> PermissionsResponse:
    """Returns the current user's role and list of fine-grained RBAC permission keys."""
    return PermissionsResponse(
        role=current_user.role,
        permissions=list(current_user.permissions),
    )
