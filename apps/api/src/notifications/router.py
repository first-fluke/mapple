from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.rate_limit import check_data_rate_limit
from src.notifications.schemas import DeviceTokenOut, DeviceTokenRegister
from src.notifications.service import DeviceTokenService

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(check_data_rate_limit)],
)


@router.post("/device-tokens", status_code=201)
async def register_device_token(
    body: DeviceTokenRegister,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DeviceTokenOut]:
    """Register (or re-register) a device token for push notifications.

    Idempotent: posting the same token again updates updated_at and platform
    without creating a duplicate row.
    """
    service = DeviceTokenService(session)
    device_token = await service.register(
        user_id=user_id,
        token=body.token,
        platform=body.platform,
    )
    return ApiResponse(data=DeviceTokenOut.model_validate(device_token))


@router.delete("/device-tokens/{token:path}", status_code=204)
async def unregister_device_token(
    token: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Unregister a device token (e.g. on logout).

    Returns 204 on success, 404 if the token is not registered for the current user.
    """
    service = DeviceTokenService(session)
    await service.unregister(user_id=user_id, token=token)


@router.get("/device-tokens")
async def list_device_tokens(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[DeviceTokenOut]]:
    """List all device tokens registered for the current user."""
    service = DeviceTokenService(session)
    tokens = await service.list_tokens(user_id=user_id)
    return ApiResponse(data=[DeviceTokenOut.model_validate(t) for t in tokens])
