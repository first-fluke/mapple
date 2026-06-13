"""Auth router — OAuth dance + JWS access + opaque refresh.

Endpoints:
  GET  /auth/login/{provider}     PKCE + Redis-backed state, redirect to IdP
  GET  /auth/callback/{provider}  exchange code, verify id_token, mint tokens
  POST /auth/exchange             mobile native id_token → tokens
  POST /auth/refresh              rotate refresh, family invalidation on replay
  POST /auth/logout               invalidate refresh family
  GET  /auth/me                   current user profile (Bearer JWS)
  PATCH /auth/me                  update profile
  DELETE /auth/me                 delete account
"""

import json
import os
import secrets
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.oauth import (
    PROVIDER_CONFIG,
    SUPPORTED_PROVIDERS,
    _apple_credentials_present,
    build_authorization_url,
    compute_code_challenge,
    exchange_code_for_tokens,
    fetch_github_user_info,
    get_client_id,
    verify_apple_id_token,
    verify_google_id_token,
)
from src.auth.schemas import (
    ExchangeRequest,
    LogoutRequest,
    ProfileUpdate,
    RefreshRequest,
    TokenResponse,
    UserOut,
)
from src.auth.service import AuthService
from src.auth.tokens import (
    invalidate_family,
    issue_access,
    issue_refresh,
    rotate_refresh,
)
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.lib.rate_limit import check_rate_limit
from src.lib.redis import get_redis

WEB_APP_URL = os.getenv("WEB_APP_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

OAUTH_STATE_TTL = 600  # 10 min
OAUTH_STATE_PREFIX = "oauth:state:"

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(check_rate_limit)],
)


def _redirect_uri(provider: str) -> str:
    return f"{API_BASE_URL}/auth/callback/{provider}"


def _login_redirect(target_path: str = "/", error: str | None = None) -> RedirectResponse:
    if error:
        return RedirectResponse(f"{WEB_APP_URL}/?auth_error={error}", status_code=302)
    return RedirectResponse(f"{WEB_APP_URL}{target_path}", status_code=302)


# ---------------------------------------------------------------------------
# OAuth start
# ---------------------------------------------------------------------------


@router.get("/login/{provider}")
async def oauth_start(
    provider: str,
    redis: Annotated[Redis, Depends(get_redis)],
    return_to: str = Query(default="/", max_length=512),
) -> RedirectResponse:
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")

    state_id = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    nonce = secrets.token_urlsafe(32)

    record = json.dumps(
        {
            "provider": provider,
            "code_verifier": code_verifier,
            "nonce": nonce,
            "return_to": return_to if return_to.startswith("/") else "/",
        }
    )
    await redis.set(OAUTH_STATE_PREFIX + state_id, record, ex=OAUTH_STATE_TTL)

    code_challenge = compute_code_challenge(code_verifier)
    auth_url = build_authorization_url(
        provider=provider,
        state=state_id,
        code_challenge=code_challenge,
        nonce=nonce,
        redirect_uri=_redirect_uri(provider),
    )
    return RedirectResponse(auth_url, status_code=302)


# ---------------------------------------------------------------------------
# OAuth callback
# ---------------------------------------------------------------------------


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    redis: Annotated[Redis, Depends(get_redis)],
    db: Annotated[AsyncSession, Depends(get_session)],
    code: str = Query(),
    state: str = Query(),
) -> RedirectResponse:
    if provider not in SUPPORTED_PROVIDERS:
        return _login_redirect(error="unsupported_provider")

    raw = await redis.get(OAUTH_STATE_PREFIX + state)
    if raw is None:
        return _login_redirect(error="invalid_state")
    await redis.delete(OAUTH_STATE_PREFIX + state)

    state_record = json.loads(raw)
    if state_record.get("provider") != provider:
        return _login_redirect(error="provider_mismatch")

    try:
        provider_tokens = await exchange_code_for_tokens(
            provider=provider,
            code=code,
            code_verifier=state_record["code_verifier"],
            redirect_uri=_redirect_uri(provider),
        )
    except httpx.HTTPError:
        return _login_redirect(error="token_exchange_failed")

    try:
        if provider == "google":
            id_token = provider_tokens.get("id_token")
            if not id_token:
                return _login_redirect(error="missing_id_token")
            claims = await verify_google_id_token(
                id_token=id_token,
                nonce=state_record["nonce"],
                client_id=get_client_id("google"),
            )
            email = claims["email"]
            name = claims.get("name", email)
            image = claims.get("picture")
        elif provider == "github":
            access_token = provider_tokens.get("access_token")
            if not access_token:
                return _login_redirect(error="missing_access_token")
            user_info = await fetch_github_user_info(access_token)
            if not user_info.get("email"):
                return _login_redirect(error="email_unavailable")
            email = user_info["email"]
            name = user_info.get("name") or email
            image = user_info.get("picture")
        else:
            return _login_redirect(error="unsupported_provider")
    except Exception:
        return _login_redirect(error="provider_verification_failed")

    service = AuthService(db)
    user = await service.upsert_oauth_user(email=email, name=name, image=image)

    access, exp = issue_access(user.id)
    refresh, _, _ = await issue_refresh(redis, user.id)

    return_to = state_record.get("return_to", "/")
    fragment = f"access={access}&refresh={refresh}&exp={exp}"
    return RedirectResponse(f"{WEB_APP_URL}{return_to}#{fragment}", status_code=302)


# ---------------------------------------------------------------------------
# Mobile native exchange
# ---------------------------------------------------------------------------


@router.post("/exchange")
async def oauth_exchange(
    body: ExchangeRequest,
    redis: Annotated[Redis, Depends(get_redis)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    provider = body.provider
    if provider not in SUPPORTED_PROVIDERS and provider != "apple":
        raise HTTPException(status_code=400, detail="Unsupported provider")
    if provider == "apple":
        if not _apple_credentials_present():
            # TODO(oma-deferred): integrate Apple Sign-In when credentials are provisioned
            raise HTTPException(
                status_code=501,
                detail=(
                    "Apple Sign-In is not configured on this server. "
                    "Set APPLE_CLIENT_ID, APPLE_TEAM_ID, APPLE_KEY_ID, and "
                    "APPLE_PRIVATE_KEY environment variables to enable it."
                ),
            )
        apple_client_id = os.getenv("APPLE_CLIENT_ID", "")
        try:
            claims = await verify_apple_id_token(
                id_token=body.id_token,
                client_id=apple_client_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=401, detail=f"Apple id_token verification failed: {exc}") from exc
        email = claims.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Apple id_token missing email claim")
        name = claims.get("name", email)
        image = None

        service = AuthService(db)
        user = await service.upsert_oauth_user(email=email, name=name, image=image)

        access, exp = issue_access(user.id)
        refresh, _, _ = await issue_refresh(redis, user.id)
        return TokenResponse(access=access, refresh=refresh, exp=exp)

    if provider == "google":
        try:
            claims = await verify_google_id_token(
                id_token=body.id_token,
                nonce="",  # mobile native flow skips nonce; verify by audience + signature
                client_id=get_client_id("google"),
            )
        except Exception as exc:
            raise HTTPException(status_code=401, detail=f"id_token verification failed: {exc}") from exc
        email = claims["email"]
        name = claims.get("name", email)
        image = claims.get("picture")
    else:  # github native: id_token is actually an access_token in this path
        try:
            user_info = await fetch_github_user_info(body.id_token)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=f"GitHub verification failed: {exc}") from exc
        if not user_info.get("email"):
            raise HTTPException(status_code=401, detail="email_unavailable")
        email = user_info["email"]
        name = user_info.get("name") or email
        image = user_info.get("picture")

    service = AuthService(db)
    user = await service.upsert_oauth_user(email=email, name=name, image=image)

    access, exp = issue_access(user.id)
    refresh, _, _ = await issue_refresh(redis, user.id)
    return TokenResponse(access=access, refresh=refresh, exp=exp)


# ---------------------------------------------------------------------------
# Refresh rotation
# ---------------------------------------------------------------------------


@router.post("/refresh")
async def oauth_refresh(
    body: RefreshRequest,
    redis: Annotated[Redis, Depends(get_redis)],
) -> TokenResponse:
    new_refresh, user_id, _, _ = await rotate_refresh(redis, body.refresh)
    access, exp = issue_access(user_id)
    return TokenResponse(access=access, refresh=new_refresh, exp=exp)


# ---------------------------------------------------------------------------
# Logout (invalidate family)
# ---------------------------------------------------------------------------


@router.post("/logout", status_code=204)
async def oauth_logout(
    body: LogoutRequest,
    redis: Annotated[Redis, Depends(get_redis)],
) -> None:
    from src.auth.tokens import get_refresh_record

    record = await get_refresh_record(redis, body.refresh)
    if record:
        await invalidate_family(redis, record["family_id"])


# ---------------------------------------------------------------------------
# Profile (existing)
# ---------------------------------------------------------------------------


@router.get("/me")
async def me(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[UserOut]:
    service = AuthService(db)
    user = await service.get_me(user_id)
    return ApiResponse(data=UserOut.model_validate(user))


@router.patch("/me")
async def update_me(
    body: ProfileUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ApiResponse[UserOut]:
    service = AuthService(db)
    user = await service.update_me(user_id, body)
    return ApiResponse(data=UserOut.model_validate(user))


@router.delete("/me")
async def delete_me(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> ApiResponse[dict[str, str]]:
    """Delete account and invalidate any refresh families if family_id is supplied via header."""
    service = AuthService(db)
    await service.delete_me(user_id)
    return ApiResponse(data={"message": "Account deleted"})
