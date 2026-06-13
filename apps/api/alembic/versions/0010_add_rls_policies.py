"""Add per-table RLS policies for user-owned rows.

Migration 0007 enabled RLS with FORCE ROW LEVEL SECURITY on all application
tables but defined no policies, leaving a default-deny that blocks every
connection including the application's own service-role queries.

This migration adds the missing policies.

## Connection / role model (src/lib/database.py)

The FastAPI application connects as the ``globe`` Postgres role (the same
role that owns all tables, specified in DATABASE_URL).  Postgres normally
bypasses RLS for the table owner, but migration 0007 set
``FORCE ROW LEVEL SECURITY``, so even the owner is subject to RLS.

There is currently **no** ``SET LOCAL app.current_user_id`` call anywhere in
the application's session lifecycle; all queries run as the single ``globe``
role with no per-request impersonation.

## Policy design

Given that the application does not set a session-level user variable, a
fine-grained "each request can only see its own rows" enforcement at the DB
layer is not possible without application changes.  The policies defined here
therefore implement **two tiers**:

1. **Service-role bypass**: A permissive ``USING (true)`` policy for the
   ``globe`` role covers every table.  This restores the application's
   ability to read and write all rows (the behaviour before 0007) while
   keeping RLS enabled as infrastructure.

2. **User-scoped policies** (for any future restricted role or PostgREST
   direct access): Policies on user-owned tables scoped to
   ``current_setting('app.current_user_id', true)`` are added but
   intentionally do **not** apply to the ``globe`` role.  If the application
   ever gains a per-request ``SET LOCAL app.current_user_id = :uid`` call,
   switching to a lower-privileged Postgres role for data queries will make
   these policies the active gate automatically.

## Tables covered

User-owned (direct user_id column):
  contact, meeting, tag, contact_relationship

User-owned (via parent FK):
  experience          → via contact.user_id
  meeting_attendee    → via meeting.user_id
  contact_tag         → via contact.user_id

Shared / no user owner:
  organization        → no user_id; readable/writable by service role only
  user                → identity table; each user can read/write their own row

## Future path

To make row-level isolation effective at the DB layer:
  1. Add ``SET LOCAL app.current_user_id = :uid`` inside the
     ``get_session()`` async generator in src/lib/database.py.
  2. Create a lower-privileged Postgres role (e.g. ``globe_app``) with
     SELECT/INSERT/UPDATE/DELETE on application tables but without table
     ownership, and switch DATABASE_URL to use that role.
  3. Remove or narrow the service-role bypass policies in this migration.

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-13
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The Postgres role used by the application (DATABASE_URL user).
_SERVICE_ROLE = "globe"


def _service_bypass(table: str, policy_name: str) -> None:
    """Create a permissive USING (true) policy restricted to the service role.

    This restores full access for the application while keeping RLS active
    as a defense-in-depth layer against external tools / lesser-privileged
    connections.
    """
    op.execute(
        f"""
        CREATE POLICY {policy_name}
            ON "{table}"
            AS PERMISSIVE
            FOR ALL
            TO {_SERVICE_ROLE}
            USING (true)
            WITH CHECK (true)
        """
    )


def _user_scoped_select(table: str, policy_name: str, using_expr: str) -> None:
    """Create a USING policy for SELECT/UPDATE/DELETE on user-owned rows.

    Not applied to the service role (which already has full access via the
    bypass policy). Applies to any other role that might be granted access
    in the future (e.g., a restricted app role or PostgREST anon/authed).
    """
    op.execute(
        f"""
        CREATE POLICY {policy_name}
            ON "{table}"
            AS PERMISSIVE
            FOR ALL
            USING ({using_expr})
            WITH CHECK ({using_expr})
        """
    )


def upgrade() -> None:
    # ------------------------------------------------------------------
    # "user" table — identity rows; each user owns their own record.
    # ------------------------------------------------------------------
    _service_bypass("user", "user_service_access")
    _user_scoped_select(
        "user",
        "user_self_access",
        "id = current_setting('app.current_user_id', true)",
    )

    # ------------------------------------------------------------------
    # contact — direct user_id column.
    # ------------------------------------------------------------------
    _service_bypass("contact", "contact_service_access")
    _user_scoped_select(
        "contact",
        "contact_user_access",
        "user_id = current_setting('app.current_user_id', true)",
    )

    # ------------------------------------------------------------------
    # meeting — direct user_id column.
    # ------------------------------------------------------------------
    _service_bypass("meeting", "meeting_service_access")
    _user_scoped_select(
        "meeting",
        "meeting_user_access",
        "user_id = current_setting('app.current_user_id', true)",
    )

    # ------------------------------------------------------------------
    # tag — direct user_id column.
    # ------------------------------------------------------------------
    _service_bypass("tag", "tag_service_access")
    _user_scoped_select(
        "tag",
        "tag_user_access",
        "user_id = current_setting('app.current_user_id', true)",
    )

    # ------------------------------------------------------------------
    # contact_relationship — direct user_id column.
    # ------------------------------------------------------------------
    _service_bypass("contact_relationship", "contact_relationship_service_access")
    _user_scoped_select(
        "contact_relationship",
        "contact_relationship_user_access",
        "user_id = current_setting('app.current_user_id', true)",
    )

    # ------------------------------------------------------------------
    # experience — scoped via parent contact.user_id.
    # Subquery: experience is visible when its contact belongs to the
    # current user.
    # ------------------------------------------------------------------
    _service_bypass("experience", "experience_service_access")
    _user_scoped_select(
        "experience",
        "experience_user_access",
        (
            "contact_id IN ("
            "  SELECT id FROM contact"
            "  WHERE user_id = current_setting('app.current_user_id', true)"
            ")"
        ),
    )

    # ------------------------------------------------------------------
    # meeting_attendee — scoped via parent meeting.user_id.
    # ------------------------------------------------------------------
    _service_bypass("meeting_attendee", "meeting_attendee_service_access")
    _user_scoped_select(
        "meeting_attendee",
        "meeting_attendee_user_access",
        (
            "meeting_id IN ("
            "  SELECT id FROM meeting"
            "  WHERE user_id = current_setting('app.current_user_id', true)"
            ")"
        ),
    )

    # ------------------------------------------------------------------
    # contact_tag — scoped via parent contact.user_id.
    # contact_tag is the SQLAlchemy ContactTag model (table "contact_tag").
    # ------------------------------------------------------------------
    _service_bypass("contact_tag", "contact_tag_service_access")
    _user_scoped_select(
        "contact_tag",
        "contact_tag_user_access",
        (
            "contact_id IN ("
            "  SELECT id FROM contact"
            "  WHERE user_id = current_setting('app.current_user_id', true)"
            ")"
        ),
    )

    # ------------------------------------------------------------------
    # organization — shared reference table, no per-user ownership.
    # Service role has full access; no other role policy needed (read-only
    # access for lesser roles could be added when PostgREST is enabled).
    # ------------------------------------------------------------------
    _service_bypass("organization", "organization_service_access")


def downgrade() -> None:
    policies = [
        ("user", "user_service_access"),
        ("user", "user_self_access"),
        ("contact", "contact_service_access"),
        ("contact", "contact_user_access"),
        ("meeting", "meeting_service_access"),
        ("meeting", "meeting_user_access"),
        ("tag", "tag_service_access"),
        ("tag", "tag_user_access"),
        ("contact_relationship", "contact_relationship_service_access"),
        ("contact_relationship", "contact_relationship_user_access"),
        ("experience", "experience_service_access"),
        ("experience", "experience_user_access"),
        ("meeting_attendee", "meeting_attendee_service_access"),
        ("meeting_attendee", "meeting_attendee_user_access"),
        ("contact_tag", "contact_tag_service_access"),
        ("contact_tag", "contact_tag_user_access"),
        ("organization", "organization_service_access"),
    ]
    for table, policy in policies:
        op.execute(f'DROP POLICY IF EXISTS {policy} ON "{table}"')
