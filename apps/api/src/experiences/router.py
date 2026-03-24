from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.experiences.schemas import ExperienceCreate, ExperienceOut, ExperienceUpdate
from src.experiences.service import ExperienceService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/contacts/{contact_id}/experiences", tags=["experiences"])


@router.get("")
async def list_experiences(
    contact_id: int,
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ExperienceOut]]:
    """List all experiences for a contact."""
    service = ExperienceService(session)
    experiences = await service.list_by_contact(contact_id)
    return ApiResponse(
        data=[ExperienceOut.model_validate(e) for e in experiences],
    )


@router.post("", status_code=201)
async def create_experience(
    contact_id: int,
    body: ExperienceCreate,
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ExperienceOut]:
    """Create a new experience for a contact."""
    service = ExperienceService(session)
    experience = await service.create(
        contact_id=contact_id,
        organization_id=body.organization_id,
        role=body.role,
        major=body.major,
    )
    return ApiResponse(data=ExperienceOut.model_validate(experience))


@router.put("/{experience_id}")
async def update_experience(
    contact_id: int,
    experience_id: int,
    body: ExperienceUpdate,
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ExperienceOut]:
    """Update an experience."""
    service = ExperienceService(session)
    experience = await service.update(
        contact_id=contact_id,
        experience_id=experience_id,
        organization_id=body.organization_id,
        role=body.role,
        major=body.major,
    )
    return ApiResponse(data=ExperienceOut.model_validate(experience))


@router.delete("/{experience_id}", status_code=204)
async def delete_experience(
    contact_id: int,
    experience_id: int,
    _user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete an experience."""
    service = ExperienceService(session)
    await service.delete(contact_id=contact_id, experience_id=experience_id)
