"""Schemas for the CSV contact import endpoint."""

import re
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator

# Reuse the same phone pattern as contacts/schemas.py.
_PHONE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,30}$")

CSV_ROW_LIMIT = 1000


class ImportRow(BaseModel):
    """A single validated row parsed from the uploaded CSV."""

    name: str
    email: EmailStr | None = None
    phone: str | None = None
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        if len(v) > 255:
            raise ValueError("name must be 255 characters or fewer")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        if v is None or v.strip() == "":
            return None
        v = v.strip()
        if not _PHONE_PATTERN.match(v):
            raise ValueError(f"phone '{v}' does not match expected format")
        if len(v) > 30:
            raise ValueError("phone must be 30 characters or fewer")
        return v

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v: object) -> object:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class ImportRowResult(BaseModel):
    """Result reported back for a single CSV row."""

    row: int
    status: Literal["created", "error"]
    error: str | None = None


class ImportSummary(BaseModel):
    """Top-level response body for POST /imports/contacts."""

    total: int
    created: int
    errors: int
    results: list[ImportRowResult]
