from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.contact_relationships.crud_service import ContactRelationshipCRUDService
from src.contact_relationships.schemas import (
    ContactRelationshipCreate,
    ContactRelationshipOut,
)
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/contact-relationships", tags=["contact-relationships"])


@router.get("/contacts/{contact_id}")
async def list_relationships_for_contact(
    contact_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ContactRelationshipOut]]:
    """List all relationships for a contact belonging to the authenticated user."""
    service = ContactRelationshipCRUDService(session)
    relationships = await service.list_for_contact(user_id, contact_id)
    return ApiResponse(
        data=[ContactRelationshipOut.model_validate(r) for r in relationships]
    )


@router.post("", status_code=201)
async def create_relationship(
    body: ContactRelationshipCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactRelationshipOut]:
    """Create or update a relationship edge between two contacts."""
    service = ContactRelationshipCRUDService(session)
    relationship = await service.create(user_id, body)
    return ApiResponse(data=ContactRelationshipOut.model_validate(relationship))


@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a relationship edge."""
    service = ContactRelationshipCRUDService(session)
    await service.delete(user_id, relationship_id)
