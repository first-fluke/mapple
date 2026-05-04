from typing import Literal

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    image: str | None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


# ---------------------------------------------------------------------------
# Token schemas
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    """Returned after login, exchange, or refresh."""
    access: str
    refresh: str
    exp: int  # Unix timestamp: access token expiry


class ExchangeRequest(BaseModel):
    """Mobile native auth — exchange a provider id_token for our tokens."""
    provider: Literal["google", "github", "apple"]
    id_token: str


class RefreshRequest(BaseModel):
    """Rotate a refresh token."""
    refresh: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    """Invalidate a refresh token family."""
    refresh: str = Field(min_length=1)
