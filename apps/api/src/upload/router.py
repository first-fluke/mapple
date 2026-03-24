from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from src.lib.auth import get_current_user_id
from src.lib.exceptions import ApiResponse, AppException
from src.lib.redis import get_redis
from src.upload.schemas import AvatarUploadRequest, PresignedUrlOut
from src.upload.service import UploadService

router = APIRouter(prefix="/upload", tags=["upload"])

AVATAR_RATE_LIMIT = 5
AVATAR_RATE_WINDOW = 60


async def check_avatar_rate_limit(
    user_id: str = Depends(get_current_user_id),
    redis: Redis = Depends(get_redis),
) -> str:
    key = f"rate:upload:avatar:{user_id}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, AVATAR_RATE_WINDOW)

    if count > AVATAR_RATE_LIMIT:
        raise AppException(
            status_code=429,
            code="RATE_LIMITED",
            message="Too many upload requests. Try again later.",
        )

    return user_id


@router.post("/avatar", status_code=201)
async def create_avatar_upload_url(
    body: AvatarUploadRequest,
    user_id: str = Depends(check_avatar_rate_limit),
) -> ApiResponse[PresignedUrlOut]:
    """Generate a presigned URL for avatar upload (5MB max, image/* only)."""
    service = UploadService()
    url, object_name, expires_in = await service.create_avatar_presigned_url(user_id, body.content_type)

    return ApiResponse(
        data=PresignedUrlOut(
            url=url,
            object_name=object_name,
            expires_in=expires_in,
        )
    )
