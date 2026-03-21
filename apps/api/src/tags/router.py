from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.tags.schemas import TagCreate, TagOut, TagUpdate
from src.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
async def list_tags(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[TagOut]]:
    """List all tags for the current user."""
    service = TagService(session)
    tags = await service.list_tags(user_id)
    return ApiResponse(data=[TagOut.model_validate(t) for t in tags])


@router.post("", status_code=201)
async def create_tag(
    body: TagCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TagOut]:
    """Create a new tag."""
    service = TagService(session)
    tag = await service.create_tag(user_id, body)
    return ApiResponse(data=TagOut.model_validate(tag))


@router.patch("/{tag_id}")
async def update_tag(
    tag_id: int,
    body: TagUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TagOut]:
    """Update a tag."""
    service = TagService(session)
    tag = await service.update_tag(user_id, tag_id, body)
    return ApiResponse(data=TagOut.model_validate(tag))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a tag."""
    service = TagService(session)
    await service.delete_tag(user_id, tag_id)
