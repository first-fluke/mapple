"""create meeting and meeting_attendee tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meeting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
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
    )
    op.create_index(
        "ix_meeting_start_time",
        "meeting",
        ["start_time"],
    )

    op.create_table(
        "meeting_attendee",
        sa.Column(
            "meeting_id",
            sa.Integer(),
            sa.ForeignKey("meeting.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            sa.Integer(),
            sa.ForeignKey("contact.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("meeting_id", "contact_id"),
    )
    op.create_index(
        "ix_meeting_attendee_contact_id",
        "meeting_attendee",
        ["contact_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_meeting_attendee_contact_id", table_name="meeting_attendee")
    op.drop_table("meeting_attendee")
    op.drop_index("ix_meeting_start_time", table_name="meeting")
    op.drop_table("meeting")
