from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from src.contacts.models import Contact


@dataclass
class GraphContactRow:
    id: int
    name: str
    avatar_url: str | None


@dataclass
class GraphLinkRow:
    contact_id_1: int
    contact_id_2: int
    # Derived org type ('company', 'school', or None when no shared org)
    org_type: str | None
    # Label: shared org name if available, otherwise the partner contact name
    label: str | None


class GraphRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_edges_by_org_type(self, org_type: str) -> list[dict]:
        """Find edges between contacts that share an organization of the given type."""
        stmt = text("""
            SELECT DISTINCT
                e1.contact_id AS source_contact_id,
                e2.contact_id AS target_contact_id,
                o.name AS label
            FROM experience e1
            JOIN experience e2
                ON e1.organization_id = e2.organization_id
                AND e1.contact_id < e2.contact_id
            JOIN organization o
                ON o.id = e1.organization_id
            WHERE o.type = :org_type
            ORDER BY o.name, e1.contact_id, e2.contact_id
        """)
        result = await self.session.execute(stmt, {"org_type": org_type})
        return [
            {
                "source_contact_id": row.source_contact_id,
                "target_contact_id": row.target_contact_id,
                "label": row.label,
            }
            for row in result
        ]

    async def find_clusters_by_org_type(self, org_type: str) -> list[dict]:
        """Find clusters of contacts grouped by organization of the given type."""
        stmt = text("""
            SELECT
                o.id,
                o.name AS label,
                array_agg(DISTINCT e.contact_id ORDER BY e.contact_id) AS contact_ids
            FROM organization o
            JOIN experience e ON e.organization_id = o.id
            WHERE o.type = :org_type
            GROUP BY o.id, o.name
            HAVING count(DISTINCT e.contact_id) >= 1
            ORDER BY o.name
        """)
        result = await self.session.execute(stmt, {"org_type": org_type})
        return [
            {
                "id": row.id,
                "label": row.label,
                "contact_ids": list(row.contact_ids),
            }
            for row in result
        ]

    async def find_graph_contacts(
        self,
        user_id: str,
        *,
        search: str | None = None,
    ) -> list[GraphContactRow]:
        """Return all non-deleted contacts for the user.

        Tags are excluded via noload to avoid the selectin overhead; the
        force-graph view only needs id / name / avatar_url.
        """
        stmt = (
            select(Contact)
            .options(noload(Contact.tags))
            .where(
                Contact.user_id == user_id,
                Contact.deleted_at.is_(None),
            )
            .order_by(Contact.id.asc())
        )
        if search:
            stmt = stmt.where(Contact.name.ilike(f"%{search}%"))

        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())
        return [
            GraphContactRow(
                id=c.id,
                name=c.name,
                avatar_url=c.avatar_url,
            )
            for c in contacts
        ]

    async def find_graph_links(
        self,
        user_id: str,
        *,
        contact_ids: list[int],
    ) -> list[GraphLinkRow]:
        """Return relationship edges among the given contact_ids owned by user_id.

        LinkType derivation (company > school > other):
        - For each relationship pair, a LEFT JOIN against experience + organization
          finds the highest-priority shared org type.
        - Priority: company (→ 'colleague') > school (→ 'classmate') > other types
          (→ 'other'). When no shared org exists the link defaults to 'friend'.
        - The org name is used as label when a shared org exists; otherwise NULL
          (service layer falls back to partner contact name).
        """
        if not contact_ids:
            return []

        # Use a parameterised ANY(:ids) so we never interpolate values into SQL.
        stmt = text("""
            WITH ranked_shared_orgs AS (
                SELECT
                    cr.id              AS rel_id,
                    cr.contact_id_1,
                    cr.contact_id_2,
                    o.name             AS org_name,
                    o.type             AS org_type,
                    CASE o.type
                        WHEN 'company' THEN 1
                        WHEN 'school'  THEN 2
                        ELSE                3
                    END                AS priority,
                    ROW_NUMBER() OVER (
                        PARTITION BY cr.id
                        ORDER BY
                            CASE o.type
                                WHEN 'company' THEN 1
                                WHEN 'school'  THEN 2
                                ELSE                3
                            END ASC
                    ) AS rn
                FROM contact_relationship cr
                LEFT JOIN experience e1
                    ON e1.contact_id = cr.contact_id_1
                LEFT JOIN experience e2
                    ON  e2.contact_id    = cr.contact_id_2
                    AND e2.organization_id = e1.organization_id
                LEFT JOIN organization o
                    ON o.id = e1.organization_id
                   AND e2.organization_id IS NOT NULL
                WHERE cr.user_id        = :user_id
                  AND cr.contact_id_1   = ANY(:ids)
                  AND cr.contact_id_2   = ANY(:ids)
            )
            SELECT
                rel_id,
                contact_id_1,
                contact_id_2,
                org_name  AS label,
                org_type
            FROM ranked_shared_orgs
            WHERE rn = 1

            UNION ALL

            -- Relationships where both contacts are in the list but no shared org
            -- exists (LEFT JOIN produced no org row → not captured above).
            SELECT
                cr.id  AS rel_id,
                cr.contact_id_1,
                cr.contact_id_2,
                NULL   AS label,
                NULL   AS org_type
            FROM contact_relationship cr
            WHERE cr.user_id      = :user_id
              AND cr.contact_id_1 = ANY(:ids)
              AND cr.contact_id_2 = ANY(:ids)
              AND cr.id NOT IN (
                  SELECT rel_id FROM ranked_shared_orgs WHERE rn = 1
              )
            ORDER BY contact_id_1, contact_id_2
        """)

        result = await self.session.execute(
            stmt,
            {"user_id": user_id, "ids": contact_ids},
        )
        return [
            GraphLinkRow(
                contact_id_1=row.contact_id_1,
                contact_id_2=row.contact_id_2,
                org_type=row.org_type,
                label=row.label,
            )
            for row in result
        ]
