from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import (
    LogoutRequest,
    RefreshRequest,
    TokenRequest,
    TokenResponse,
    UserOut,
)
from src.auth.service import AuthService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.rate_limit import check_rate_limit
from src.lib.redis import get_redis

router = APIRouter(
    prefix="/auth", tags=["auth"], dependencies=[Depends(check_rate_limit)]
)


@router.get("/callback")
async def callback(
    code: str,
    state: str | None = None,
) -> ApiResponse[dict[str, str | None]]:
    """Receive OAuth redirect from provider."""
    return ApiResponse(data={"code": code, "state": state})


@router.post("/token")
async def token(
    body: TokenRequest,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[TokenResponse]:
    """Exchange OAuth authorization code for JWT tokens."""
    service = AuthService(session, redis)
    result = await service.exchange_token(body.provider, body.code, body.redirect_uri)
    return ApiResponse(data=TokenResponse(**result))


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[TokenResponse]:
    """Refresh JWT using refresh token."""
    service = AuthService(session, redis)
    result = await service.refresh(body.refresh_token)
    return ApiResponse(data=TokenResponse(**result))


@router.delete("/logout")
async def logout(
    body: LogoutRequest,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[dict[str, str]]:
    """Invalidate refresh token."""
    service = AuthService(session, redis)
    await service.logout(body.refresh_token)
    return ApiResponse(data={"message": "Logged out"})


@router.get("/me")
async def me(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ApiResponse[UserOut]:
    """Get current user profile."""
    service = AuthService(session, redis)
    user = await service.get_me(user_id)
    return ApiResponse(data=UserOut.model_validate(user))
