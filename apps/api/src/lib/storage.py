import os

from miniopy_async import Minio  # type: ignore[attr-defined]

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

ENV = os.getenv("ENV", "dev")
_IS_DEV = ENV in ("dev", "local", "test")

_access_key = os.getenv("MINIO_ACCESS_KEY", "")
_secret_key = os.getenv("MINIO_SECRET_KEY", "")

if not _access_key or not _secret_key:
    if _IS_DEV:
        # Use insecure defaults only in dev/local/test environments
        _access_key = _access_key or "minioadmin"
        _secret_key = _secret_key or "minioadmin"
    else:
        raise RuntimeError(
            "MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set in production. "
            "Set ENV=dev to allow insecure dev defaults."
        )

storage = Minio(
    MINIO_ENDPOINT,
    access_key=_access_key,
    secret_key=_secret_key,
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
