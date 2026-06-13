from typing import Literal

from pydantic import BaseModel, Field

ALLOWED_AVATAR_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})

# Use Literal so pydantic validates against exact allowed values
AvatarContentType = Literal["image/jpeg", "image/png", "image/webp"]


class AvatarUploadRequest(BaseModel):
    content_type: AvatarContentType = Field(
        examples=["image/png", "image/jpeg", "image/webp"],
    )


class AvatarConfirmRequest(BaseModel):
    object_name: str = Field(min_length=1, max_length=512)
    contact_id: int


class PresignedUrlOut(BaseModel):
    url: str
    object_name: str
    expires_in: int
