"""migrate to better-auth tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create better-auth tables
    op.create_table(
        "user",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("emailVerified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "session",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False, unique=True),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("ipAddress", sa.Text(), nullable=True),
        sa.Column("userAgent", sa.Text(), nullable=True),
        sa.Column(
            "userId",
            sa.Text(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_index("ix_session_token", "session", ["token"])
    op.create_index("ix_session_userId", "session", ["userId"])

    op.create_table(
        "account",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("accountId", sa.Text(), nullable=False),
        sa.Column("providerId", sa.Text(), nullable=False),
        sa.Column(
            "userId",
            sa.Text(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("accessToken", sa.Text(), nullable=True),
        sa.Column("refreshToken", sa.Text(), nullable=True),
        sa.Column("idToken", sa.Text(), nullable=True),
        sa.Column("accessTokenExpiresAt", sa.DateTime(), nullable=True),
        sa.Column("refreshTokenExpiresAt", sa.DateTime(), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("password", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_account_userId", "account", ["userId"])

    op.create_table(
        "verification",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("identifier", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 2. Migrate existing user_auth data to better-auth tables
    op.execute("""
        INSERT INTO "user" (id, name, email, "emailVerified", image, "createdAt", "updatedAt")
        SELECT
            id::text,
            COALESCE(name, email),
            email,
            true,
            avatar_url,
            created_at,
            updated_at
        FROM user_auth
        ON CONFLICT (email) DO NOTHING
    """)

    op.execute("""
        INSERT INTO account (id, "accountId", "providerId", "userId", "createdAt", "updatedAt")
        SELECT
            id::text || '_acc',
            provider_id,
            provider,
            id::text,
            created_at,
            updated_at
        FROM user_auth
    """)

    # 3. Update domain table FK columns from INTEGER to TEXT
    # contact
    op.drop_constraint("fk_contact_user_id", "contact", type_="foreignkey")
    op.drop_index("ix_contact_user_id", table_name="contact")
    op.execute("ALTER TABLE contact ALTER COLUMN user_id TYPE text USING user_id::text")
    op.create_foreign_key("fk_contact_user_id", "contact", "user", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_contact_user_id", "contact", ["user_id"])

    # meeting
    op.drop_constraint("fk_meeting_user_id", "meeting", type_="foreignkey")
    op.drop_index("ix_meeting_user_id", table_name="meeting")
    op.execute("ALTER TABLE meeting ALTER COLUMN user_id TYPE text USING user_id::text")
    op.create_foreign_key("fk_meeting_user_id", "meeting", "user", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_meeting_user_id", "meeting", ["user_id"])

    # tag
    op.drop_constraint("fk_tag_user_id", "tag", type_="foreignkey")
    op.drop_constraint("uq_tag_user_name", "tag", type_="unique")
    op.execute("ALTER TABLE tag ALTER COLUMN user_id TYPE text USING user_id::text")
    op.create_foreign_key("fk_tag_user_id", "tag", "user", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_unique_constraint("uq_tag_user_name", "tag", ["user_id", "name"])

    # contact_relationship
    op.drop_constraint("uq_contact_relationship_pair", "contact_relationship", type_="unique")
    op.execute(
        "ALTER TABLE contact_relationship ALTER COLUMN user_id TYPE text USING user_id::text"
    )
    op.create_unique_constraint(
        "uq_contact_relationship_pair",
        "contact_relationship",
        ["user_id", "contact_id_1", "contact_id_2"],
    )

    # 4. Drop old tables
    op.drop_table("user_auth")
    op.drop_table("users")


def downgrade() -> None:
    # Recreate old tables
    op.create_table(
        "user_auth",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("provider_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "provider_id", name="uq_user_auth_provider"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Revert domain table FK columns (data loss for non-numeric IDs)
    for table in ("contact", "meeting", "tag", "contact_relationship"):
        op.execute(f"DELETE FROM {table} WHERE user_id !~ '^[0-9]+$'")

    op.drop_constraint("fk_contact_user_id", "contact", type_="foreignkey")
    op.drop_index("ix_contact_user_id", table_name="contact")
    op.execute("ALTER TABLE contact ALTER COLUMN user_id TYPE integer USING user_id::integer")
    op.create_foreign_key("fk_contact_user_id", "contact", "user_auth", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_contact_user_id", "contact", ["user_id"])

    op.drop_constraint("fk_meeting_user_id", "meeting", type_="foreignkey")
    op.drop_index("ix_meeting_user_id", table_name="meeting")
    op.execute("ALTER TABLE meeting ALTER COLUMN user_id TYPE integer USING user_id::integer")
    op.create_foreign_key("fk_meeting_user_id", "meeting", "user_auth", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_meeting_user_id", "meeting", ["user_id"])

    op.drop_constraint("fk_tag_user_id", "tag", type_="foreignkey")
    op.drop_constraint("uq_tag_user_name", "tag", type_="unique")
    op.execute("ALTER TABLE tag ALTER COLUMN user_id TYPE integer USING user_id::integer")
    op.create_foreign_key("fk_tag_user_id", "tag", "user_auth", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_unique_constraint("uq_tag_user_name", "tag", ["user_id", "name"])

    op.drop_constraint("uq_contact_relationship_pair", "contact_relationship", type_="unique")
    op.execute(
        "ALTER TABLE contact_relationship ALTER COLUMN user_id TYPE integer USING user_id::integer"
    )
    op.create_unique_constraint(
        "uq_contact_relationship_pair",
        "contact_relationship",
        ["user_id", "contact_id_1", "contact_id_2"],
    )

    # Drop better-auth tables
    op.drop_table("verification")
    op.drop_table("account")
    op.drop_table("session")
    op.drop_table("user")
