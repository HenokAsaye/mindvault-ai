"""make_organization_required_field

Revision ID: 10df2a717cda
Revises: 20260502_0003
Create Date: 2026-05-06 08:12:16.822591
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "10df2a717cda"
down_revision = "20260502_0003"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.drop_index(
        op.f("ix_org_invitations_email"), table_name="organization_invitations"
    )
    op.drop_index(
        op.f("ix_org_invitations_org_id"), table_name="organization_invitations"
    )
    op.drop_index(
        op.f("uq_org_invitations_org_email_pending"),
        table_name="organization_invitations",
        postgresql_where="(consumed_at IS NULL)",
    )
    op.create_index(
        op.f("ix_organization_invitations_email"),
        "organization_invitations",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_invitations_org_id"),
        "organization_invitations",
        ["org_id"],
        unique=False,
    )
    op.drop_index(op.f("ix_membership_org_id"), table_name="organization_memberships")
    op.drop_index(op.f("ix_membership_user_id"), table_name="organization_memberships")
    op.create_index(
        op.f("ix_organization_memberships_org_id"),
        "organization_memberships",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_memberships_user_id"),
        "organization_memberships",
        ["user_id"],
        unique=False,
    )
    op.drop_constraint(op.f("refresh_tokens_jti_key"), "refresh_tokens", type_="unique")

def downgrade() -> None:
    op.create_unique_constraint(
        op.f("refresh_tokens_jti_key"),
        "refresh_tokens",
        ["jti"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_index(
        op.f("ix_organization_memberships_user_id"),
        table_name="organization_memberships",
    )
    op.drop_index(
        op.f("ix_organization_memberships_org_id"),
        table_name="organization_memberships",
    )
    op.create_index(
        op.f("ix_membership_user_id"),
        "organization_memberships",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_membership_org_id"),
        "organization_memberships",
        ["org_id"],
        unique=False,
    )
    op.drop_index(
        op.f("ix_organization_invitations_org_id"),
        table_name="organization_invitations",
    )
    op.drop_index(
        op.f("ix_organization_invitations_email"), table_name="organization_invitations"
    )
    op.create_index(
        op.f("uq_org_invitations_org_email_pending"),
        "organization_invitations",
        ["org_id", "email"],
        unique=True,
        postgresql_where="(consumed_at IS NULL)",
    )
    op.create_index(
        op.f("ix_org_invitations_org_id"),
        "organization_invitations",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_org_invitations_email"),
        "organization_invitations",
        ["email"],
        unique=False,
    )
