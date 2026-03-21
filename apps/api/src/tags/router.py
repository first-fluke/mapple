from typing import Any

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.tags.schemas import TagCreate, TagOut, TagUpdate
from src.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
async def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ApiResponse[list[TagOut]]:
    service = TagService(session)
    return await service.list_tags(
        current_user["sub"], page=page, per_page=per_page
    )


@router.post("", status_code=201)
async def create_tag(
    body: TagCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ApiResponse[TagOut]:
    service = TagService(session)
    tag = await service.create_tag(body, current_user["sub"])
    return ApiResponse(data=tag)


@router.get("/{tag_id}")
async def get_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ApiResponse[TagOut]:
    service = TagService(session)
    tag = await service.get_tag(tag_id, current_user["sub"])
    return ApiResponse(data=tag)


@router.put("/{tag_id}")
async def update_tag(
    tag_id: int,
    body: TagUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ApiResponse[TagOut]:
    service = TagService(session)
    tag = await service.update_tag(tag_id, body, current_user["sub"])
    return ApiResponse(data=tag)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    service = TagService(session)
    await service.delete_tag(tag_id, current_user["sub"])
    return Response(status_code=204)


contact_tag_router = APIRouter(prefix="/contacts", tags=["contact-tags"])


@contact_tag_router.post("/{contact_id}/tags/{tag_id}", status_code=201)
async def attach_tag(
    contact_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ApiResponse[dict]:
    service = TagService(session)
    await service.attach_tag(contact_id, tag_id, current_user["sub"])
    return ApiResponse(data={"contact_id": contact_id, "tag_id": tag_id})


@contact_tag_router.delete("/{contact_id}/tags/{tag_id}", status_code=204)
async def detach_tag(
    contact_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    service = TagService(session)
    await service.detach_tag(contact_id, tag_id, current_user["sub"])
    return Response(status_code=204)
