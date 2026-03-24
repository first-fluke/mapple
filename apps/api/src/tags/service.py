from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import NotFoundException
from src.tags.models import Tag
from src.tags.repository import TagRepository
from src.tags.schemas import TagCreate, TagUpdate


class TagService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TagRepository(session)

    async def list_tags(self, user_id: str) -> list[Tag]:
        return await self.repo.find_by_user(user_id)

    async def create_tag(self, user_id: str, data: TagCreate) -> Tag:
        return await self.repo.create(
            user_id=user_id,
            name=data.name,
            color=data.color,
        )

    async def update_tag(self, user_id: str, tag_id: int, data: TagUpdate) -> Tag:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException(message=f"Tag {tag_id} not found")
        return await self.repo.update(
            tag,
            name=data.name,
            color=data.color,
        )

    async def delete_tag(self, user_id: str, tag_id: int) -> None:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException(message=f"Tag {tag_id} not found")
        await self.repo.delete(tag)
