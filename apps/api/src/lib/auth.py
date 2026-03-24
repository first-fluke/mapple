import datetime

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.database import get_session
from src.lib.exceptions import UnauthorizedException

COOKIE_NAME = "better-auth.session_token"
SECURE_COOKIE_NAME = "__Secure-better-auth.session_token"


async def get_current_user_id(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> str:
    token = _extract_session_token(request)
    if not token:
        raise UnauthorizedException(message="Missing session token")

    result = await session.execute(
        text(
            'SELECT "userId" FROM "session" '
            'WHERE token = :token AND "expiresAt" > :now'
        ),
        {"token": token, "now": datetime.datetime.now(datetime.UTC)},
    )
    row = result.first()
    if not row:
        raise UnauthorizedException(message="Invalid or expired session")

    return row[0]


def _extract_session_token(request: Request) -> str | None:
    token = request.cookies.get(COOKIE_NAME) or request.cookies.get(SECURE_COOKIE_NAME)
    if token:
        return token

    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None
