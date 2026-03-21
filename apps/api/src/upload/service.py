import uuid
from datetime import timedelta

from src.lib.storage import storage

AVATAR_BUCKET = "avatars"
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
PRESIGNED_EXPIRY = timedelta(minutes=10)


class UploadService:
    async def _ensure_bucket(self) -> None:
        if not await storage.bucket_exists(AVATAR_BUCKET):
            await storage.make_bucket(AVATAR_BUCKET)

    async def create_avatar_presigned_url(self, user_id: int, content_type: str) -> tuple[str, str, int]:
        await self._ensure_bucket()

        ext = content_type.split("/")[-1]
        object_name = f"{user_id}/{uuid.uuid4()}.{ext}"

        url = await storage.presigned_put_object(
            AVATAR_BUCKET,
            object_name,
            expires=PRESIGNED_EXPIRY,
        )

        return url, object_name, int(PRESIGNED_EXPIRY.total_seconds())
