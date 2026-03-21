from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import NotFoundException
from src.tags.models import Tag
from src.tags.repository import TagRepository
from src.tags.schemas import TagCreate, TagUpdate


class TagService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TagRepository(session)

    async def list_by_user(self, user_id: int) -> list[Tag]:
        return await self.repo.find_by_user(user_id)

    async def create(self, *, user_id: int, name: str) -> Tag:
        existing = await self.repo.find_by_name(name, user_id)
        if existing:
            return existing
        return await self.repo.create(user_id=user_id, name=name)

    async def delete(self, *, tag_id: int, user_id: int) -> None:
    async def list_tags(self, user_id: int) -> list[Tag]:
    async def create_tag(self, user_id: int, data: TagCreate) -> Tag:
        return await self.repo.create(
            user_id=user_id,
            name=data.name,
            color=data.color,
        )
    async def update_tag(self, user_id: int, tag_id: int, data: TagUpdate) -> Tag:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException(message=f"Tag {tag_id} not found")
        return await self.repo.update(
            tag,
    async def delete_tag(self, user_id: int, tag_id: int) -> None:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException(message=f"Tag {tag_id} not found")
        await self.repo.delete(tag)
