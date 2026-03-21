"""create organization table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("name", "type", name="uq_organization_name_type"),
    )
    op.create_index(
        "ix_organization_name",
        "organization",
        [sa.text("lower(name) varchar_pattern_ops")],
    )


def downgrade() -> None:
    op.drop_index("ix_organization_name", table_name="organization")
    op.drop_table("organization")
