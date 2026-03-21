from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.tags.schemas import TagCreate, TagOut
from src.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
async def list_tags(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[TagOut]]:
    """List all tags for the current user."""
    service = TagService(session)
    tags = await service.list_by_user(user_id)
    return ApiResponse(data=[TagOut.model_validate(t) for t in tags])


@router.post("", status_code=201)
async def create_tag(
    body: TagCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TagOut]:
    """Create a tag (idempotent — returns existing if name matches)."""
    service = TagService(session)
    tag = await service.create(user_id=user_id, name=body.name)
    return ApiResponse(data=TagOut.model_validate(tag))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a tag."""
    service = TagService(session)
    await service.delete(tag_id=tag_id, user_id=user_id)
