from pydantic import BaseModel


class TokenRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    provider: str
    email: str
    name: str | None
    avatar_url: str | None

    model_config = {"from_attributes": True}
