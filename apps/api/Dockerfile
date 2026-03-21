# syntax=docker/dockerfile:1

# --- Build stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first for layer caching
COPY uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-group dev

# Copy source and install the project itself
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-group dev

# --- Runtime stage ---
FROM python:3.14-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create non-root user
RUN groupadd --system app && useradd --system --gid app app

# Copy the virtual environment from the builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application source
COPY --chown=app:app src/ src/

# Ensure venv binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

USER app

EXPOSE 8080

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8080"]
