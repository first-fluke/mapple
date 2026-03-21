
from pydantic import BaseModel

from src.lib.exceptions import ApiResponse


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


def paginate[T](
    items: list[T],
    *,
    page: int,
    per_page: int,
    total: int,
) -> ApiResponse[list[T]]:
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
    )
    return ApiResponse(data=items, meta=meta.model_dump())


class CursorMeta(BaseModel):
    per_page: int
    next_cursor: str | None = None
    has_more: bool


def paginate_cursor[T](
    items: list[T],
    *,
    per_page: int,
    next_cursor: str | None,
    has_more: bool,
) -> ApiResponse[list[T]]:
    meta = CursorMeta(
        per_page=per_page,
        next_cursor=next_cursor,
        has_more=has_more,
    )
    return ApiResponse(data=items, meta=meta.model_dump())
