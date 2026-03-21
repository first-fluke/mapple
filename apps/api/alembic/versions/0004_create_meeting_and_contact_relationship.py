"""create meeting and contact_relationship tables

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
    op.create_table(
        "meeting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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

    op.create_table(
        "meeting_participant",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["meeting_id"],
            ["meeting.id"],
            name="fk_meeting_participant_meeting_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.id"],
            name="fk_meeting_participant_contact_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "meeting_id", "contact_id", name="uq_meeting_participant"
        ),
    )
    op.create_index(
        "ix_meeting_participant_meeting_id",
        "meeting_participant",
        ["meeting_id"],
    )
    op.create_index(
        "ix_meeting_participant_contact_id",
        "meeting_participant",
        ["contact_id"],
    )

    op.create_table(
        "contact_relationship",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("contact_id_1", sa.Integer(), nullable=False),
        sa.Column("contact_id_2", sa.Integer(), nullable=False),
        sa.Column("strength", sa.Float(), nullable=False),
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
            name="fk_contact_relationship_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id_1"],
            ["contact.id"],
            name="fk_contact_relationship_contact_id_1",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id_2"],
            ["contact.id"],
            name="fk_contact_relationship_contact_id_2",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "contact_id_1",
            "contact_id_2",
            name="uq_contact_relationship_pair",
        ),
        sa.CheckConstraint(
            "contact_id_1 < contact_id_2",
            name="ck_contact_relationship_ordered",
        ),
        sa.CheckConstraint(
            "strength > 0",
            name="ck_contact_relationship_positive_strength",
        ),
    )
    op.create_index(
        "ix_contact_relationship_user_id",
        "contact_relationship",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_contact_relationship_user_id", table_name="contact_relationship")
    op.drop_table("contact_relationship")
    op.drop_index("ix_meeting_participant_contact_id", table_name="meeting_participant")
    op.drop_index("ix_meeting_participant_meeting_id", table_name="meeting_participant")
    op.drop_table("meeting_participant")
    op.drop_index("ix_meeting_user_id", table_name="meeting")
    op.drop_table("meeting")
