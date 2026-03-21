# Globe CRM API

FastAPI backend for Globe CRM.

## Architecture

```
apps/api/
├── pyproject.toml
├── alembic.ini
├── alembic/              # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── src/
│   ├── main.py           # FastAPI application entrypoint
│   ├── lib/              # Shared utilities
│   │   ├── auth.py       # JWT authentication
│   │   ├── database.py   # SQLAlchemy async engine & session
│   │   ├── exceptions.py # Error handling & response envelopes
│   │   ├── pagination.py # Offset & cursor pagination
│   │   ├── redis.py      # Redis client
│   │   └── storage.py    # MinIO object storage client
│   └── <domain>/         # Feature modules (see pattern below)
│       ├── router.py
│       ├── service.py
│       ├── repository.py
│       ├── schemas.py
│       └── models.py
└── AGENTS.md
```

## Router → Service → Repository Pattern

Each feature domain follows a three-layer architecture:

| Layer        | Responsibility                          | Depends On     |
| ------------ | --------------------------------------- | -------------- |
| **Router**   | HTTP handling, request/response mapping | Service        |
| **Service**  | Business logic, orchestration           | Repository     |
| **Repository** | Data access, queries                  | SQLAlchemy     |

### Rules

- **Router** receives Pydantic schemas, calls Service, returns `ApiResponse`.
- **Service** contains business rules. No direct DB access — delegate to Repository.
- **Repository** uses SQLAlchemy async sessions. Returns model instances or scalars.
- Dependencies flow downward only: Router → Service → Repository.
- Cross-domain calls go through the Service layer, never directly to another Repository.

### Example

```python
# src/contacts/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.contacts.schemas import ContactOut
from src.contacts.service import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ContactOut]:
    service = ContactService(session)
    contact = await service.get(contact_id)
    return ApiResponse(data=contact)
```

## Response Envelope

### Success

```json
{
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 100, "total_pages": 5 },
  "errors": null
}
```

### Error

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": null
  }
}
```

## Commands

```bash
# Install dependencies
uv sync

# Run dev server
uv run fastapi dev src/main.py

# Run migrations
uv run alembic upgrade head

# Create migration
uv run alembic revision --autogenerate -m "description"
```

## Conventions

- Python 3.12+, async/await throughout
- Use `Depends()` for dependency injection (session, auth, services)
- All database models inherit from `src.lib.database.Base`
- Raise `AppException` subclasses for domain errors — never return raw HTTP errors
- Use `ApiResponse[T]` for all endpoint return types
