"""Create device_token table for FCM push notification registration.

Adds the device_token table that stores per-user FCM/APNS/Web push tokens.
A unique constraint on (user_id, token) enables idempotent upsert via
INSERT ... ON CONFLICT DO UPDATE.

RLS follows the two-tier pattern established in migration 0010:
  1. Service-role bypass: USING (true) for the ``globe`` owner role so that
     the application can read/write all rows while FORCE RLS remains active.
  2. User-scoped policy: scoped to current_setting('app.current_user_id')
     for any future restricted role (PostgREST, etc.).

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SERVICE_ROLE = "globe"
_TABLE = "device_token"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_device_token_user_id",
        _TABLE,
        ["user_id"],
    )
    op.create_unique_constraint(
        "uq_device_token_user_token",
        _TABLE,
        ["user_id", "token"],
    )

    # Enable RLS with FORCE so the service role is also subject to policies.
    op.execute(f'ALTER TABLE "{_TABLE}" ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{_TABLE}" FORCE ROW LEVEL SECURITY')

    # Tier 1: service-role bypass (restores full access for the app).
    op.execute(
        f"""
        CREATE POLICY device_token_service_access
            ON "{_TABLE}"
            AS PERMISSIVE
            FOR ALL
            TO {_SERVICE_ROLE}
            USING (true)
            WITH CHECK (true)
        """
    )

    # Tier 2: user-scoped policy for any future restricted / PostgREST role.
    op.execute(
        f"""
        CREATE POLICY device_token_user_access
            ON "{_TABLE}"
            AS PERMISSIVE
            FOR ALL
            USING (user_id = current_setting('app.current_user_id', true))
            WITH CHECK (user_id = current_setting('app.current_user_id', true))
        """
    )


def downgrade() -> None:
    op.execute(f'DROP POLICY IF EXISTS device_token_user_access ON "{_TABLE}"')
    op.execute(f'DROP POLICY IF EXISTS device_token_service_access ON "{_TABLE}"')
    op.drop_table(_TABLE)
