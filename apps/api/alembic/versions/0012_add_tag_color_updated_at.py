"""Add color and updated_at to the tag table.

Drift fix: the Tag model declares `color` (VARCHAR(7), default '#6366f1') and
`updated_at`, but migration 0004 created the `tag` table without them. Tag
colors are used by the UI (tag chips) and mirrored onto contact_tag.color, so
the model is correct and the migration was missing these columns. This aligns
the migrated schema with the model.

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tag",
        sa.Column(
            "color",
            sa.String(7),
            server_default=sa.text("'#6366f1'"),
            nullable=False,
        ),
    )
    op.add_column(
        "tag",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tag", "updated_at")
    op.drop_column("tag", "color")
