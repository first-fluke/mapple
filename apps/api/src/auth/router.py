from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import (
    ProfileUpdate,
    UserOut,
)
from src.auth.service import AuthService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[UserOut]:
    """Get current user profile."""
    service = AuthService(session)
    user = await service.get_me(user_id)
    return ApiResponse(data=UserOut.model_validate(user))


@router.patch("/me")
async def update_me(
    body: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[UserOut]:
    """Update current user profile."""
    service = AuthService(session)
    user = await service.update_me(user_id, body)
    return ApiResponse(data=UserOut.model_validate(user))


@router.delete("/me")
async def delete_me(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, str]]:
    """Delete current user account."""
    service = AuthService(session)
    await service.delete_me(user_id)
    return ApiResponse(data={"message": "Account deleted"})
