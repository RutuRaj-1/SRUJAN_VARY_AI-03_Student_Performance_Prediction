"""
Security utilities, Supabase JWT verification via JWKS (ES256/RS256),
and Role-Based Access Control (RBAC) dependencies.
"""
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache
from typing import Callable, List, Optional, Set
import uuid

import jwt
from jwt import PyJWKClient, PyJWKClientError
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.enums import UserRole, AccountStatus
from app.models.profile import Profile

settings = get_settings()

_jwks_client = None


def get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client
    if _jwks_client is None and settings.SUPABASE_URL:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        try:
            _jwks_client = PyJWKClient(jwks_url, cache_keys=True, max_cached_keys=16)
        except Exception as exc:
            logger.warning("Could not initialize JWKS client for %s: %s", jwks_url, exc)
            _jwks_client = None
    return _jwks_client


# Role Permissions Matrix
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: {
        "platform:manage",
        "institutions:create",
        "institutions:read",
        "institutions:update",
        "institutions:delete",
        "users:manage",
        "system:diagnostics",
    },
    UserRole.INSTITUTION_ADMIN: {
        "institution:read",
        "institution:update",
        "members:manage",
        "members:approve",
        "members:suspend",
        "curriculum:oversight",
        "analytics:institution",
    },
    UserRole.FACULTY: {
        "syllabus:upload",
        "syllabus:approve",
        "assessments:create",
        "assessments:review",
        "interventions:approve",
        "risk:view_alerts",
        "students:view_cohort",
    },
    UserRole.PLACEMENT_OFFICER: {
        "career:roles:manage",
        "career:benchmarks:view",
        "career:readiness:cohort",
        "students:competencies:view",
    },
    UserRole.STUDENT: {
        "profile:self:read",
        "profile:self:update",
        "assessments:attempt",
        "mastery:self:read",
        "interventions:self:read",
        "career:self:read",
    },
}


def get_permissions_for_role(role: UserRole) -> Set[str]:
    return ROLE_PERMISSIONS.get(role, set())


class CurrentUser:
    """Represents the authenticated and verified identity in request context."""
    def __init__(
        self,
        user_id: str,
        email: str,
        role: UserRole,
        account_status: AccountStatus,
        full_name: str,
        institution_id: Optional[str] = None,
        raw_claims: Optional[dict] = None,
    ):
        self.user_id = str(user_id)
        self.email = email
        self.role = role
        self.account_status = account_status
        self.full_name = full_name
        self.institution_id = str(institution_id) if institution_id else None
        self.raw_claims = raw_claims or {}
        self.permissions = get_permissions_for_role(role)

    def has_role(self, *required_roles: UserRole) -> bool:
        if self.role == UserRole.SUPER_ADMIN:
            return True
        return self.role in required_roles

    def has_permission(self, permission: str) -> bool:
        if self.role == UserRole.SUPER_ADMIN:
            return True
        return permission in self.permissions

    @property
    def is_active(self) -> bool:
        return self.account_status == AccountStatus.ACTIVE


def decode_and_verify_supabase_jwt(token: str) -> dict:
    """
    Cryptographically verifies Supabase Auth JWT access tokens.
    Supports ES256 / RS256 via JWKS endpoint, with fallback to secret key for HS256.
    """
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_settings = get_settings()

    # 1. In testing mode, if token is an automated test token, decode directly
    if current_settings.APP_ENV == "testing":
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid test token format.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Attempt verification via JWKS (Asymmetric ES256 / RS256)
    jwks_client = get_jwks_client()
    expected_issuer = f"{current_settings.SUPABASE_URL.rstrip('/')}/auth/v1" if current_settings.SUPABASE_URL else None

    if jwks_client:
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256", "HS256"],
                audience="authenticated",
                issuer=expected_issuer,
                options={"verify_exp": True, "verify_aud": True},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.InvalidTokenError, PyJWKClientError) as exc:
            logger.debug("JWKS validation failed, checking secret key fallback: %s", exc)

    # 3. Fallback to Supabase Secret Key (HS256)
    secret_key = current_settings.effective_secret_key
    if secret_key:
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"],
                audience="authenticated",
                options={"verify_exp": True, "verify_aud": False},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify authentication credentials with Supabase Auth.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Optional[Session] = Depends(get_db),
) -> CurrentUser:
    """
    Extracts Bearer token, verifies JWT with Supabase, loads authoritative
    user profile from database (or provisions default), and returns CurrentUser.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ", 1)[1].strip()
    payload = decode_and_verify_supabase_jwt(token)

    user_id = payload.get("sub")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing required subject (sub) or email claims.",
        )

    # Query profile from database if DB is configured and accessible
    profile = None
    if db:
        try:
            parsed_uuid = uuid.UUID(user_id)
            profile = db.query(Profile).filter(Profile.id == parsed_uuid).first()

            # Automatic fallback provisioning if profile does not exist in DB yet
            meta = payload.get("user_metadata", {})
            inst_id = None
            if meta.get("institution_id"):
                try:
                    inst_id = uuid.UUID(meta["institution_id"])
                except (ValueError, TypeError):
                    pass

            if not profile:
                full_name = meta.get("full_name") or email.split("@")[0]
                status_str = meta.get("account_status", AccountStatus.PENDING.value)
                role_str = meta.get("role", UserRole.STUDENT.value)
                profile = Profile(
                    id=parsed_uuid,
                    full_name=full_name,
                    email=email,
                    role=role_str,
                    account_status=status_str,
                    institution_id=inst_id,
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
                logger.info("Auto-provisioned profile for user %s (%s)", user_id, email)
            else:
                # Sync metadata updates if present
                updated = False
                if meta.get("account_status") and profile.account_status != meta.get("account_status"):
                    profile.account_status = meta["account_status"]
                    updated = True
                if meta.get("role") and profile.role != meta.get("role"):
                    profile.role = meta["role"]
                    updated = True
                if inst_id and profile.institution_id != inst_id:
                    profile.institution_id = inst_id
                    updated = True
                if updated:
                    db.commit()
                    db.refresh(profile)
        except Exception as exc:
            logger.warning("Database profile lookup error for user %s: %s", user_id, exc)
            if db:
                db.rollback()

    if profile:
        try:
            user_role = UserRole(profile.role)
        except ValueError:
            user_role = UserRole.STUDENT
        try:
            account_status = AccountStatus(profile.account_status)
        except ValueError:
            account_status = AccountStatus.PENDING

        return CurrentUser(
            user_id=str(profile.id),
            email=profile.email,
            role=user_role,
            account_status=account_status,
            full_name=profile.full_name,
            institution_id=str(profile.institution_id) if profile.institution_id else None,
            raw_claims=payload,
        )

    # Standalone fallback if DB is not wired: construct user context from claims
    meta = payload.get("user_metadata", {})
    claim_role_str = meta.get("role") or payload.get("app_metadata", {}).get("role", "STUDENT")
    try:
        user_role = UserRole(claim_role_str)
    except ValueError:
        user_role = UserRole.STUDENT

    claim_status_str = meta.get("account_status", "ACTIVE" if user_role == UserRole.SUPER_ADMIN else "PENDING")
    try:
        account_status = AccountStatus(claim_status_str)
    except ValueError:
        account_status = AccountStatus.PENDING

    return CurrentUser(
        user_id=user_id,
        email=email,
        role=user_role,
        account_status=account_status,
        full_name=meta.get("full_name") or email.split("@")[0],
        institution_id=meta.get("institution_id"),
        raw_claims=payload,
    )


def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Ensures the authenticated user has an ACTIVE account status."""
    if current_user.account_status == AccountStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending institutional approval. Please contact your institution administrator.",
        )
    if current_user.account_status in (AccountStatus.SUSPENDED, AccountStatus.DISABLED):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your account is {current_user.account_status.value.lower()}. Access denied.",
        )
    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable[[CurrentUser], CurrentUser]:
    """Dependency factory checking if current user possesses one of the allowed roles."""
    def role_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if not current_user.has_role(*allowed_roles):
            role_names = ", ".join([r.value for r in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. This resource requires one of the following roles: [{role_names}]. Current role: {current_user.role.value}",
            )
        return current_user
    return role_checker


def require_institution_access(
    institution_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """Enforces that the user belongs to or administers the specified institution."""
    if current_user.role == UserRole.SUPER_ADMIN:
        return current_user
    if current_user.institution_id != str(institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to institutional records outside your designated institution.",
        )
    return current_user
