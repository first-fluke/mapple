import csv
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.contacts.models import Contact
from src.experiences.models import Experience
from src.organizations.models import Organization


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def export_contacts_csv(self, user_id: int) -> str:
        org = aliased(Organization)

        stmt = (
            select(
                Contact.name,
                Contact.email,
                Contact.phone,
                org.name.label("organization"),
                Experience.role,
                Experience.major,
            )
            .outerjoin(Experience, Experience.contact_id == Contact.id)
            .outerjoin(org, org.id == Experience.organization_id)
            .where(Contact.user_id == user_id)
            .order_by(Contact.name)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "email", "phone", "organization", "role", "major"])

        for row in rows:
            writer.writerow([
                row.name or "",
                row.email or "",
                row.phone or "",
                row.organization or "",
                row.role or "",
                row.major or "",
            ])

        return output.getvalue()
