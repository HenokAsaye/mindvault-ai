"""organization_invitations for durable IAM invites

Revision ID: 20260502_0003
Revises: 20260429_0002
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260502_0003"
down_revision = "20260429_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organization_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("invited_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_org_invitations_org_id",
        "organization_invitations",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        "ix_org_invitations_email", "organization_invitations", ["email"], unique=False
    )
    op.create_index(
        "uq_org_invitations_org_email_pending",
        "organization_invitations",
        ["org_id", "email"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_org_invitations_org_email_pending", table_name="organization_invitations"
    )
    op.drop_index("ix_org_invitations_email", table_name="organization_invitations")
    op.drop_index("ix_org_invitations_org_id", table_name="organization_invitations")
    op.drop_table("organization_invitations")
