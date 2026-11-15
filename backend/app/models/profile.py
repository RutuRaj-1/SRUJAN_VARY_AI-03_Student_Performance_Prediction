import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import UserRole, AccountStatus


class Profile(Base, TimestampMixin):
    """
    Connects Supabase Auth identities (auth.users) with application user profiles.
    The profile ID matches the Supabase Auth user ID.
    """
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=UserRole.STUDENT.value, index=True
    )
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("institutions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    account_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AccountStatus.PENDING.value, index=True
    )

    # Relationships
    institution: Mapped[Optional["Institution"]] = relationship(
        "Institution", back_populates="profiles"
    )
    memberships: Mapped[List["InstitutionMembership"]] = relationship(
        "InstitutionMembership", back_populates="profile", cascade="all, delete-orphan"
    )
