from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


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
