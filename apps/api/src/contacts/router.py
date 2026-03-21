from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.schemas import (
    ContactCreate,
    ContactOut,
    ContactUpdate,
    ExperienceOut,
    TagOut,
)
from src.contacts.service import ContactService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _to_contact_out(data: dict) -> ContactOut:
    contact = data["contact"]
    return ContactOut(
        id=contact.id,
        user_id=contact.user_id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        latitude=contact.latitude,
        longitude=contact.longitude,
        country=contact.country,
        city=contact.city,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        tags=[TagOut.model_validate(t) for t in data["tags"]],
        experiences=[ExperienceOut.model_validate(e) for e in data["experiences"]],
    )


@router.get("")
async def list_contacts(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactOut]]:
    """List all contacts for the current user."""
    service = ContactService(session)
    items = await service.list_by_user(user_id)
    return ApiResponse(data=[_to_contact_out(item) for item in items])


@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Get a single contact."""
    service = ContactService(session)
    data = await service.get(contact_id=contact_id, user_id=user_id)
    return ApiResponse(data=_to_contact_out(data))


@router.post("", status_code=201)
async def create_contact(
    body: ContactCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Create a new contact with optional tags and experiences."""
    service = ContactService(session)
    data = await service.create(
        user_id=user_id,
        name=body.name,
        email=body.email,
        phone=body.phone,
        latitude=body.latitude,
        longitude=body.longitude,
        country=body.country,
        city=body.city,
        tag_ids=body.tag_ids,
        experiences=body.experiences,
    )
    return ApiResponse(data=_to_contact_out(data))


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    """Update a contact."""
    service = ContactService(session)
    data = await service.update(
        contact_id=contact_id,
        user_id=user_id,
        name=body.name,
        email=body.email,
        phone=body.phone,
        latitude=body.latitude,
        longitude=body.longitude,
        country=body.country,
        city=body.city,
        tag_ids=body.tag_ids,
    )
    return ApiResponse(data=_to_contact_out(data))


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a contact."""
    service = ContactService(session)
    await service.delete(contact_id=contact_id, user_id=user_id)
