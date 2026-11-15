import uuid
from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Institution(Base, TimestampMixin):
    """Represents higher education institutions and university entities."""
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    institution_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Autonomous Engineering Institute"
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="India")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    profiles: Mapped[List["Profile"]] = relationship(
        "Profile", back_populates="institution", lazy="selectin"
    )
    memberships: Mapped[List["InstitutionMembership"]] = relationship(
        "InstitutionMembership", back_populates="institution", cascade="all, delete-orphan"
    )


class InstitutionMembership(Base, TimestampMixin):
    """User-to-institution relationship supporting multi-institution scope."""
    __tablename__ = "institution_memberships"
    __table_args__ = (
        UniqueConstraint("institution_id", "user_id", name="uq_institution_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    membership_role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="STUDENT"
    )
    membership_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )

    # Relationships
    institution: Mapped["Institution"] = relationship(
        "Institution", back_populates="memberships"
    )
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="memberships"
    )
