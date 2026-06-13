"""Fix meeting columns: rename start_time->starts_at, end_time->ends_at, drop scheduled_at.

The model and all service/repo/router code already use starts_at/ends_at.
The DB had start_time, end_time, and a redundant scheduled_at column.
This migration aligns the DB with the code.

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old index on start_time before renaming
    op.drop_index("ix_meeting_start_time", table_name="meeting")

    # Rename columns to match the model and API contract
    op.alter_column("meeting", "start_time", new_column_name="starts_at")
    op.alter_column("meeting", "end_time", new_column_name="ends_at")

    # Drop the redundant scheduled_at column (never used by service/repo/router)
    op.drop_column("meeting", "scheduled_at")

    # Recreate the index under the new column name
    op.create_index("ix_meeting_starts_at", "meeting", ["starts_at"])


def downgrade() -> None:
    op.drop_index("ix_meeting_starts_at", table_name="meeting")

    op.alter_column("meeting", "starts_at", new_column_name="start_time")
    op.alter_column("meeting", "ends_at", new_column_name="end_time")

    op.add_column(
        "meeting",
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
    )

    op.create_index("ix_meeting_start_time", "meeting", ["start_time"])
