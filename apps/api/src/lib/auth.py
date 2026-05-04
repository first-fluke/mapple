"""Bearer JWT dependency for FastAPI routes.

Cookie 기반 세션 로직을 완전히 제거하고 HS256 JWS access token 검증으로 대체합니다.
JWT_SIGNING_KEY 환경변수 누락/길이 부족 시 애플리케이션 시작 실패(fail-fast).
"""

import os

from fastapi import Depends, Request

from src.lib.exceptions import UnauthorizedException

# ---------------------------------------------------------------------------
# Config — fail-fast on startup
# ---------------------------------------------------------------------------

JWT_SIGNING_KEY: str = os.getenv("JWT_SIGNING_KEY", "")
JWT_ALGORITHM: str = "HS256"
JWT_ISSUER: str = "globe-crm-api"
JWT_AUDIENCE: str = "globe-crm-web"

# Kept for backward compat with conftest / security tests
JWT_SECRET: str = JWT_SIGNING_KEY

if not JWT_SIGNING_KEY or len(JWT_SIGNING_KEY.encode()) < 32:
    raise RuntimeError(
        "JWT_SIGNING_KEY environment variable must be set and at least 32 bytes long. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


async def get_current_user_id(request: Request) -> str:
    """Extract and verify Bearer JWS access token.

    Returns the user_id (sub claim) on success.
    Raises UnauthorizedException on missing/invalid/expired token.
    """
    import jwt  # imported here to keep module-level imports lean

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedException(message="Missing or invalid Authorization header")

    token = auth_header[len("Bearer "):]
    if not token:
        raise UnauthorizedException(message="Empty bearer token")

    try:
        payload = jwt.decode(
            token,
            JWT_SIGNING_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["sub", "exp", "iat", "jti", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Access token expired")
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException(message=f"Invalid access token: {exc}")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Token missing sub claim")

    return user_id


# ---------------------------------------------------------------------------
# Test helpers (kept for backward compat with existing tests)
# ---------------------------------------------------------------------------

JWT_TEST_SECRET: str = JWT_SIGNING_KEY
