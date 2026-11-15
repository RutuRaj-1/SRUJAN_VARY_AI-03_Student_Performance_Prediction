"""Initial authentication and institutions schema

Revision ID: 001_initial_auth
Revises: 
Create Date: 2026-11-15 12:20:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_auth"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Institutions
    op.create_table(
        "institutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("institution_code", sa.String(length=50), nullable=False),
        sa.Column("institution_type", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False, server_default="India"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_code", name="uq_institution_code"),
    )
    op.create_index("ix_institutions_code", "institutions", ["institution_code"])

    # 2. Profiles (matches auth.users(id))
    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="STUDENT"),
        sa.Column("institution_id", sa.Uuid(), nullable=True),
        sa.Column("account_status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("email", name="uq_profile_email"),
    )
    op.create_index("ix_profiles_email", "profiles", ["email"])
    op.create_index("ix_profiles_role", "profiles", ["role"])
    op.create_index("ix_profiles_status", "profiles", ["account_status"])

    # 3. Institution Memberships
    op.create_table(
        "institution_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("membership_role", sa.String(length=50), nullable=False, server_default="STUDENT"),
        sa.Column("membership_status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "user_id", name="uq_institution_user"),
    )
    op.create_index("ix_memberships_institution", "institution_memberships", ["institution_id"])
    op.create_index("ix_memberships_user", "institution_memberships", ["user_id"])


def downgrade() -> None:
    op.drop_table("institution_memberships")
    op.drop_table("profiles")
    op.drop_table("institutions")
