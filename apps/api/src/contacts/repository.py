import base64

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user_paginated(
        self,
        user_id: int,
        *,
        cursor: str | None = None,
        per_page: int = 20,
        search: str | None = None,
        sort: str = "created_at_desc",
        has_email: bool | None = None,
        has_phone: bool | None = None,
    ) -> tuple[list[Contact], str | None, bool]:
        stmt = select(Contact).where(Contact.user_id == user_id)

        if search:
            stmt = stmt.where(Contact.name.ilike(f"%{search}%"))

        if has_email is True:
            stmt = stmt.where(Contact.email.isnot(None), Contact.email != "")
        if has_phone is True:
            stmt = stmt.where(Contact.phone.isnot(None), Contact.phone != "")

        match sort:
            case "name_asc":
                stmt = stmt.order_by(Contact.name.asc(), Contact.id.asc())
            case "name_desc":
                stmt = stmt.order_by(Contact.name.desc(), Contact.id.desc())
            case "created_at_asc":
                stmt = stmt.order_by(Contact.created_at.asc(), Contact.id.asc())
            case _:
                stmt = stmt.order_by(Contact.created_at.desc(), Contact.id.desc())

        offset = _decode_cursor(cursor) if cursor else 0
        stmt = stmt.offset(offset).limit(per_page + 1)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        has_more = len(items) > per_page
        if has_more:
            items = items[:per_page]

        next_cursor = _encode_cursor(offset + per_page) if has_more else None

        return items, next_cursor, has_more

    async def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Contact).where(Contact.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


def _encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode()).decode()


def _decode_cursor(cursor: str) -> int:
    try:
        return int(base64.urlsafe_b64decode(cursor).decode())
    except Exception:
        return 0
