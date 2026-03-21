import os

from fastapi import Depends, Request
from redis.asyncio import Redis

from src.lib.exceptions import AppException
from src.lib.redis import get_redis

RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "10"))
RATE_WINDOW = int(os.getenv("AUTH_RATE_WINDOW", "60"))


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
