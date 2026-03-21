import os
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.lib.exceptions import UnauthorizedException

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError as e:
        raise UnauthorizedException(message=str(e)) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    return decode_token(credentials.credentials)


async def get_current_user_id(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> int:
    return int(current_user["sub"])
