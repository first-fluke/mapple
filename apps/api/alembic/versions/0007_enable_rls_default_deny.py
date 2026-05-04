"""Enable RLS + FORCE RLS on all application tables (default deny).

FastAPI uses the postgres service-role connection (DATABASE_URL with full
privileges), which bypasses RLS by default. RLS here is defense-in-depth
against Supabase PostgREST/Realtime accidental exposure: with no policies
attached, anon/authenticated roles get zero rows.

If we ever need PostgREST/Realtime, define explicit per-row policies (e.g.
`USING (user_id = auth.uid())`) instead of the empty default-deny.

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-04 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Application tables in the public schema. Keep this list in sync with model
# additions. Tables created by future migrations should also call ENABLE RLS.
TABLES = (
    "contact",
    "contact_relationship",
    "contact_tag",
    "experience",
    "meeting",
    "meeting_attendee",
    "organization",
    "tag",
    "user",
    "session",
    "account",
    "verification",
)


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY')


def downgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')
