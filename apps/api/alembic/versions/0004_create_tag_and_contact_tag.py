"""create tag and contact_tag tables

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
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_auth.id"],
            name="fk_tag_user_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
    )
    op.create_index("ix_tag_user_id", "tag", ["user_id"])

    op.create_table(
        "contact_tag",
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column(
            "color",
            sa.String(7),
            nullable=False,
            server_default="'#6366f1'",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("contact_id", "tag_id"),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.id"],
            name="fk_contact_tag_contact_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
            name="fk_contact_tag_tag_id",
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("contact_tag")
    op.drop_index("ix_tag_user_id", table_name="tag")
    op.drop_table("tag")
