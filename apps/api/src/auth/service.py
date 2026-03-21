import datetime
import os
import secrets
from typing import Any

import httpx
import jwt
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserAuth
from src.auth.repository import AuthRepository
from src.lib.auth import JWT_ALGORITHM, JWT_SECRET
from src.lib.exceptions import AppException, UnauthorizedException

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAIL_URL = "https://api.github.com/user/emails"


class AuthService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.repo = AuthRepository(session)
        self.redis = redis

    async def exchange_token(
        self, provider: str, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        user_info = await self._fetch_oauth_user(provider, code, redirect_uri)

        user = await self.repo.find_by_provider(provider, user_info["provider_id"])
        if not user:
            user = await self.repo.create(
                provider=provider,
                provider_id=user_info["provider_id"],
                email=user_info["email"],
                name=user_info.get("name"),
                avatar_url=user_info.get("avatar_url"),
            )

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        key = f"refresh:{refresh_token}"
        user_id = await self.redis.get(key)
        if not user_id:
            raise UnauthorizedException(message="Invalid or expired refresh token")

        user = await self.repo.find_by_id(int(user_id))
        if not user:
            raise UnauthorizedException(message="User not found")

        # Rotate refresh token
        await self.redis.delete(key)

        access_token = self._create_access_token(user)
        new_refresh_token = await self._create_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout(self, refresh_token: str) -> None:
        await self.redis.delete(f"refresh:{refresh_token}")

    async def get_me(self, user_id: int) -> UserAuth:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(message="User not found")
        return user

    def _create_access_token(self, user: UserAuth) -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    async def _create_refresh_token(self, user: UserAuth) -> str:
        token = secrets.token_urlsafe(32)
        key = f"refresh:{token}"
        ttl = REFRESH_TOKEN_EXPIRE_DAYS * 86400
        await self.redis.set(key, str(user.id), ex=ttl)
        return token

    async def _fetch_oauth_user(
        self, provider: str, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        if provider == "google":
            return await self._fetch_google_user(code, redirect_uri)
        if provider == "github":
            return await self._fetch_github_user(code)
        raise AppException(
            code="INVALID_PROVIDER",
            message=f"Unsupported provider: {provider}",
        )

    async def _fetch_google_user(
        self, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise AppException(
                    code="OAUTH_ERROR", message="Failed to exchange Google token"
                )

            access_token = token_resp.json()["access_token"]

            user_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_resp.status_code != 200:
                raise AppException(
                    code="OAUTH_ERROR", message="Failed to fetch Google user info"
                )

            data = user_resp.json()
            return {
                "provider_id": str(data["id"]),
                "email": data["email"],
                "name": data.get("name"),
                "avatar_url": data.get("picture"),
            }

    async def _fetch_github_user(self, code: str) -> dict[str, Any]:
        client_id = os.getenv("GITHUB_CLIENT_ID", "")
        client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")

        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            if token_resp.status_code != 200:
                raise AppException(
                    code="OAUTH_ERROR", message="Failed to exchange GitHub token"
                )

            token_data = token_resp.json()
            if "error" in token_data:
                raise AppException(
                    code="OAUTH_ERROR",
                    message=token_data.get("error_description", "OAuth error"),
                )

            access_token = token_data["access_token"]
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            user_resp = await client.get(GITHUB_USER_URL, headers=headers)
            if user_resp.status_code != 200:
                raise AppException(
                    code="OAUTH_ERROR", message="Failed to fetch GitHub user info"
                )

            user_data = user_resp.json()
            email = user_data.get("email")

            if not email:
                email_resp = await client.get(GITHUB_EMAIL_URL, headers=headers)
                if email_resp.status_code == 200:
                    emails = email_resp.json()
                    primary = next((e for e in emails if e.get("primary")), None)
                    if primary:
                        email = primary["email"]
                    elif emails:
                        email = emails[0]["email"]

            if not email:
                raise AppException(
                    code="OAUTH_ERROR",
                    message="Could not retrieve email from GitHub",
                )

            return {
                "provider_id": str(user_data["id"]),
                "email": email,
                "name": user_data.get("name") or user_data.get("login"),
                "avatar_url": user_data.get("avatar_url"),
            }
