import os
from functools import lru_cache

from miniopy_async import Minio  # type: ignore[attr-defined]

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:11900")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

ENV = os.getenv("ENV", "dev")
_IS_DEV = ENV in ("dev", "local", "test")


@lru_cache(maxsize=1)
def get_storage() -> Minio:
    """Lazily build the S3/MinIO client on first use.

    Avatar upload is the only feature that needs object storage. Building the
    client here (instead of at import time) lets the app boot in production with
    ``avatar_url`` treated as a plain URL string; the prod credential check only
    fires if the avatar-upload endpoint is actually called.
    """
    access_key = os.getenv("MINIO_ACCESS_KEY", "")
    secret_key = os.getenv("MINIO_SECRET_KEY", "")

    if not access_key or not secret_key:
        if _IS_DEV:
            # Use insecure defaults only in dev/local/test environments
            access_key = access_key or "minioadmin"
            secret_key = secret_key or "minioadmin"
        else:
            raise RuntimeError(
                "MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set to use avatar "
                "upload in production. Set them, or persist avatar_url as a plain URL."
            )

    return Minio(
        MINIO_ENDPOINT,
        access_key=access_key,
        secret_key=secret_key,
        secure=MINIO_SECURE,
    )

# Public base URL for serving stored objects (e.g. a CDN or the MinIO/B2 host).
# Falls back to the MinIO endpoint scheme when not explicitly configured.
MINIO_PUBLIC_URL = os.getenv(
    "MINIO_PUBLIC_URL",
    f"{'https' if MINIO_SECURE else 'http'}://{MINIO_ENDPOINT}",
).rstrip("/")


def public_url(bucket: str, object_name: str) -> str:
    """Return the public URL for an object stored in the given bucket."""
    return f"{MINIO_PUBLIC_URL}/{bucket}/{object_name}"
