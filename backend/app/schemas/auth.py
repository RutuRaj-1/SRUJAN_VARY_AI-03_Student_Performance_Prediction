from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole, AccountStatus, MembershipStatus, MembershipRole


class UserMeResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    account_status: AccountStatus
    institution_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)


class PermissionsResponse(BaseModel):
    role: UserRole
    permissions: List[str]


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=1024)


class InstitutionResponse(BaseModel):
    id: str
    name: str
    institution_code: str
    institution_type: str
    city: str
    state: str
    country: str
    is_active: bool
    created_at: datetime


class InstitutionMemberResponse(BaseModel):
    id: str
    institution_id: str
    user_id: str
    full_name: str
    email: str
    membership_role: str
    membership_status: str
    created_at: datetime


class MemberStatusUpdate(BaseModel):
    membership_status: MembershipStatus
    membership_role: Optional[MembershipRole] = None
