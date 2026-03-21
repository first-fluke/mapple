from pydantic import BaseModel, Field


class AvatarUploadRequest(BaseModel):
    content_type: str = Field(
        pattern=r"^image/",
        examples=["image/png", "image/jpeg", "image/webp"],
    )


class PresignedUrlOut(BaseModel):
    url: str
    object_name: str
    expires_in: int
