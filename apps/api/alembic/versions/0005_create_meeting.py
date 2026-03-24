"""create meeting and meeting_attendee tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meeting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_auth.id"],
            name="fk_meeting_user_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_meeting_user_id", "meeting", ["user_id"])
    op.create_index("ix_meeting_start_time", "meeting", ["start_time"])

    op.create_table(
        "meeting_attendee",
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("meeting_id", "contact_id"),
        sa.ForeignKeyConstraint(
            ["meeting_id"],
            ["meeting.id"],
            name="fk_meeting_attendee_meeting_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.id"],
            name="fk_meeting_attendee_contact_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_meeting_attendee_contact_id",
        "meeting_attendee",
        ["contact_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_meeting_attendee_contact_id", table_name="meeting_attendee"
    )
    op.drop_table("meeting_attendee")
    op.drop_index("ix_meeting_start_time", table_name="meeting")
    op.drop_index("ix_meeting_user_id", table_name="meeting")
    op.drop_table("meeting")
