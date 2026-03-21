from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.schemas import ContactOut
from src.contacts.service import ContactService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.pagination import paginate_cursor

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def list_contacts(
    cursor: str | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    sort: str = Query(default="created_at_desc"),
    has_email: bool | None = Query(default=None),
    has_phone: bool | None = Query(default=None),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactOut]]:
    """List contacts with cursor pagination, search, and filters."""
    service = ContactService(session)
    contacts, next_cursor, has_more = await service.list_contacts(
        user_id,
        cursor=cursor,
        per_page=per_page,
        search=search,
        sort=sort,
        has_email=has_email,
        has_phone=has_phone,
    )
    return paginate_cursor(
        [ContactOut.model_validate(c) for c in contacts],
        per_page=per_page,
        next_cursor=next_cursor,
        has_more=has_more,
    )
