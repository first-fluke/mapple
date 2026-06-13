import os

from fastapi import Depends, Request
from redis.asyncio import Redis

from src.lib.exceptions import AppException
from src.lib.redis import get_redis

RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "10"))
RATE_WINDOW = int(os.getenv("AUTH_RATE_WINDOW", "60"))

# Data endpoints: more generous than auth since these carry authenticated user context.
DATA_RATE_LIMIT = int(os.getenv("DATA_RATE_LIMIT", "120"))
DATA_RATE_WINDOW = int(os.getenv("DATA_RATE_WINDOW", "60"))


async def check_rate_limit(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:auth:{client_ip}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, RATE_WINDOW)

    if count > RATE_LIMIT:
        raise AppException(
            status_code=429,
            code="RATE_LIMITED",
            message="Too many requests. Try again later.",
        )


async def check_data_rate_limit(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    """Per-authenticated-user rate limit for data read/write endpoints.

    Keys by user ID extracted from the Authorization header so that different
    users never share a bucket. Falls back to client IP when no Bearer token
    is present (request will fail auth later; this just prevents Redis errors).
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        # Use a hash of the raw token as the bucket identifier so we do not
        # store the token value in Redis keys. User ID is not decoded here to
        # avoid duplicating JWT logic — token hash is sufficient for isolation.
        import hashlib

        token = auth_header[len("Bearer "):]
        bucket = hashlib.sha256(token.encode()).hexdigest()[:16]
        key = f"rate:data:user:{bucket}"
    else:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:data:ip:{client_ip}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, DATA_RATE_WINDOW)

    if count > DATA_RATE_LIMIT:
        raise AppException(
            status_code=429,
            code="RATE_LIMITED",
            message="Too many requests. Try again later.",
        )
