"""Drop better-auth session/account/verification tables.

After moving auth to FastAPI Authlib + JWS + Redis-backed refresh, these
better-auth tables are dead. The "user" table stays — it's still the FK
target for contact.user_id and we upsert into it on OAuth callback.

If a future provider linking feature needs per-provider account records,
add a user_oauth_account table in a follow-up migration.

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-04 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("verification")
    op.drop_table("account")
    op.drop_table("session")


def downgrade() -> None:
    op.create_table(
        "session",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False, unique=True),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("ipAddress", sa.Text(), nullable=True),
        sa.Column("userAgent", sa.Text(), nullable=True),
        sa.Column(
            "userId",
            sa.Text(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_table(
        "account",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("accountId", sa.Text(), nullable=False),
        sa.Column("providerId", sa.Text(), nullable=False),
        sa.Column(
            "userId",
            sa.Text(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("accessToken", sa.Text(), nullable=True),
        sa.Column("refreshToken", sa.Text(), nullable=True),
        sa.Column("idToken", sa.Text(), nullable=True),
        sa.Column("accessTokenExpiresAt", sa.DateTime(), nullable=True),
        sa.Column("refreshTokenExpiresAt", sa.DateTime(), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("password", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "verification",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("identifier", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
