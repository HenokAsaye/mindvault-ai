"""enterprise iam tables and columns

Revision ID: 20260429_0002
Revises: 20260428_0001
Create Date: 2026-04-29 00:00:02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260429_0002"
down_revision = "20260428_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_family", sa.String(length=64), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("replaced_by_jti", sa.String(length=64), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index(
        "ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False
    )
    op.create_index(
        "ix_refresh_tokens_org_id", "refresh_tokens", ["org_id"], unique=False
    )
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)
    op.create_index(
        "ix_refresh_tokens_token_family",
        "refresh_tokens",
        ["token_family"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_user_family",
        "refresh_tokens",
        ["user_id", "token_family"],
        unique=False,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_logs_event_type", "audit_logs", ["event_type"], unique=False
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"], unique=False)
    op.create_index("ix_audit_logs_org_id", "audit_logs", ["org_id"], unique=False)
    op.create_index(
        "ix_audit_logs_target_user_id", "audit_logs", ["target_user_id"], unique=False
    )

    op.create_index(
        "ix_membership_org_status",
        "organization_memberships",
        ["org_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_membership_org_status", table_name="organization_memberships")

    op.drop_index("ix_audit_logs_target_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_org_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_refresh_user_family", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_family", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_org_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_column("users", "mfa_enabled")
