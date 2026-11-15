"""
Security utilities and authentication abstraction.
In Phase 01, this defines the role constants, permission interfaces, and safe header extraction.
Subsequent phases will plug in Supabase JWT verification and RBAC enforcement.
"""
from enum import Enum
from typing import Optional, List
from fastapi import Header, HTTPException, status


class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
    CAREER_COUNSELOR = "career_counselor"


class CurrentUser:
    def __init__(
        self,
        user_id: str,
        email: str,
        roles: List[UserRole],
        is_active: bool = True
    ):
        self.user_id = user_id
        self.email = email
        self.roles = roles
        self.is_active = is_active

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles or UserRole.ADMIN in self.roles


def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[CurrentUser]:
    """
    Non-blocking current user extractor.
    Returns None if no token or invalid token, allowing public/health endpoints to function.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    # Token verification hook for future auth phases
    return None
