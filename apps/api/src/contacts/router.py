from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.schemas import ContactCreate, ContactOut, ContactPatch, ContactUpdate
from src.contacts.service import ContactService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def list_contacts(
    tag: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
    q: str | None = Query(default=None),
    per_page: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactOut]]:
    service = ContactService(session)
    return await service.list(
        user_id=user_id,
        per_page=per_page,
        cursor=cursor,
        tag=tag,
        country=country,
        city=city,
        q=q,
    )


@router.post("", status_code=201)
async def create_contact(
    body: ContactCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    service = ContactService(session)
    contact = await service.create(user_id=user_id, data=body)
    await session.commit()
    return ApiResponse(data=contact)


@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    service = ContactService(session)
    contact = await service.get(user_id=user_id, contact_id=contact_id)
    return ApiResponse(data=contact)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    service = ContactService(session)
    contact = await service.update(user_id=user_id, contact_id=contact_id, data=body)
    await session.commit()
    return ApiResponse(data=contact)


@router.patch("/{contact_id}")
async def patch_contact(
    contact_id: int,
    body: ContactPatch,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    service = ContactService(session)
    contact = await service.patch(user_id=user_id, contact_id=contact_id, data=body)
    await session.commit()
    return ApiResponse(data=contact)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = ContactService(session)
    await service.delete(user_id=user_id, contact_id=contact_id)
    await session.commit()
