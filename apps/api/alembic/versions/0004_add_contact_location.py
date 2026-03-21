"""add location geometry column to contact

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contact",
        sa.Column(
            "location",
            Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_contact_location",
        "contact",
        ["location"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("ix_contact_location", table_name="contact")
    op.drop_column("contact", "location")
