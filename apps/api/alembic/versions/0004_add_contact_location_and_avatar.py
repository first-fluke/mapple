"""add location and avatar columns to contact

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contact", sa.Column("avatar_url", sa.String(512), nullable=True))
    op.add_column("contact", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("contact", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("contact", "longitude")
    op.drop_column("contact", "latitude")
    op.drop_column("contact", "avatar_url")
