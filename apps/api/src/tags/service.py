from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.exceptions import ConflictException, NotFoundException
from src.lib.pagination import paginate
from src.tags.models import Tag
from src.tags.repository import TagRepository
from src.tags.schemas import TagCreate, TagOut, TagUpdate


class TagService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TagRepository(session)

    async def list_tags(self, user_id: str, *, page: int, per_page: int):
        tags, total = await self.repo.find_all(user_id, page=page, per_page=per_page)
        items = [TagOut.model_validate(t) for t in tags]
        return paginate(items, page=page, per_page=per_page, total=total)

    async def get_tag(self, tag_id: int, user_id: str) -> TagOut:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException("Tag not found")
        return TagOut.model_validate(tag)

    async def create_tag(self, data: TagCreate, user_id: str) -> TagOut:
        existing = await self.repo.find_by_name(user_id, data.name)
        if existing:
            raise ConflictException("Tag with this name already exists")

        tag = Tag(user_id=user_id, name=data.name, color=data.color)
        tag = await self.repo.create(tag)
        await self.session.commit()
        return TagOut.model_validate(tag)

    async def update_tag(
        self, tag_id: int, data: TagUpdate, user_id: str
    ) -> TagOut:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException("Tag not found")

        if data.name is not None and data.name != tag.name:
            existing = await self.repo.find_by_name(user_id, data.name)
            if existing:
                raise ConflictException("Tag with this name already exists")
            tag.name = data.name

        if "color" in data.model_fields_set:
            tag.color = data.color

        tag = await self.repo.update(tag)
        await self.session.commit()
        return TagOut.model_validate(tag)

    async def delete_tag(self, tag_id: int, user_id: str) -> None:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException("Tag not found")
        await self.repo.delete(tag)
        await self.session.commit()

    async def attach_tag(
        self, contact_id: int, tag_id: int, user_id: str
    ) -> None:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException("Tag not found")

        existing = await self.repo.find_contact_tag(contact_id, tag_id)
        if existing:
            raise ConflictException("Tag already attached to contact")

        await self.repo.attach_contact(contact_id, tag_id)
        await self.session.commit()

    async def detach_tag(
        self, contact_id: int, tag_id: int, user_id: str
    ) -> None:
        tag = await self.repo.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundException("Tag not found")

        removed = await self.repo.detach_contact(contact_id, tag_id)
        if not removed:
            raise NotFoundException("Tag not attached to contact")
        await self.session.commit()
