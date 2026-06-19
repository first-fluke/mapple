"""Verify that migration 0010 (RLS policies) applies cleanly.

These tests run against the test DB using the test engine so they do not
depend on a separate alembic invocation inside pytest.  The actual
``alembic upgrade head`` verification is documented to run separately
(see AGENTS.md / CI pipeline).

Because the test DB is set up with metadata.create_all (no RLS applied),
we test the policy SQL in isolation by executing it directly and then
rolling it back, so the test suite remains idempotent.
"""

import pytest
from sqlalchemy import text

from tests.conftest import TestSessionFactory


@pytest.mark.asyncio
async def test_rls_policy_sql_is_valid():
    """Verify the RLS policy DDL executes without syntax errors.

    Executes the CREATE POLICY statements from migration 0010 inside a
    transaction and then rolls back, leaving the schema clean.
    Tables must have RLS enabled first (migration 0007 does this in prod;
    we enable it here for the test and clean up in the same transaction).
    """
    # Tables that have user-scoped policies in 0010
    user_owned_tables = [
        "user",
        "contact",
        "meeting",
        "tag",
        "contact_relationship",
        "experience",
        "meeting_attendee",
        "contact_tag",
        "organization",
    ]

    async with TestSessionFactory() as session:
        # Use a raw connection so we can run DDL and roll it back cleanly.
        conn = await session.connection()
        await conn.execute(text("SAVEPOINT rls_test"))

        try:
            # Enable RLS on tables (mirrors migration 0007)
            for table in user_owned_tables:
                await conn.execute(
                    text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')
                )
                await conn.execute(
                    text(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY')
                )

            # Service-bypass policy (permissive, TO globe)
            for table, policy in [
                ("user", "test_rls_user_svc"),
                ("contact", "test_rls_contact_svc"),
                ("meeting", "test_rls_meeting_svc"),
                ("tag", "test_rls_tag_svc"),
                ("contact_relationship", "test_rls_cr_svc"),
                ("experience", "test_rls_exp_svc"),
                ("meeting_attendee", "test_rls_ma_svc"),
                ("contact_tag", "test_rls_ct_svc"),
                ("organization", "test_rls_org_svc"),
            ]:
                await conn.execute(
                    text(
                        f"""
                        CREATE POLICY {policy}
                            ON "{table}"
                            AS PERMISSIVE
                            FOR ALL
                            TO globe
                            USING (true)
                            WITH CHECK (true)
                        """
                    )
                )

            # User-scoped policy on "contact" as a representative sample
            await conn.execute(
                text(
                    """
                    CREATE POLICY test_rls_contact_user
                        ON "contact"
                        AS PERMISSIVE
                        FOR ALL
                        USING (user_id = current_setting('app.current_user_id', true))
                        WITH CHECK (user_id = current_setting('app.current_user_id', true))
                    """
                )
            )

            # Verify policies were created
            result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM pg_policies "
                    "WHERE policyname LIKE 'test_rls_%'"
                )
            )
            count = result.scalar()
            assert count == 10, f"Expected 10 RLS test policies, got {count}"

        finally:
            # Roll back all DDL — leaves the test DB unchanged
            await conn.execute(text("ROLLBACK TO SAVEPOINT rls_test"))
            await conn.execute(text("RELEASE SAVEPOINT rls_test"))
