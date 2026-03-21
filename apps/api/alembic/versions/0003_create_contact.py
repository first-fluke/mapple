"""create contact table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contact",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organization.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
        "ix_contact_name",
        "contact",
        [sa.text("lower(name) varchar_pattern_ops")],
    )
    op.create_index(
        "ix_contact_organization_id",
        "contact",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_contact_organization_id", table_name="contact")
    op.drop_index("ix_contact_name", table_name="contact")
    op.drop_table("contact")
