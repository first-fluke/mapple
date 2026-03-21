"""add contact location fields

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
    op.add_column("contact", sa.Column("lat", sa.Float(), nullable=True))
    op.add_column("contact", sa.Column("lng", sa.Float(), nullable=True))
    op.add_column("contact", sa.Column("avatar_url", sa.String(500), nullable=True))
    op.create_index("ix_contact_lat_lng", "contact", ["lat", "lng"])


def downgrade() -> None:
    op.drop_index("ix_contact_lat_lng", table_name="contact")
    op.drop_column("contact", "avatar_url")
    op.drop_column("contact", "lng")
    op.drop_column("contact", "lat")
