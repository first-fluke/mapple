"""Import service — validates CSV rows and delegates to ContactRepository."""

import csv
import io
import re

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.repository import ContactRepository
from src.imports.schemas import CSV_ROW_LIMIT, ImportRow, ImportRowResult, ImportSummary

# Tags may be separated by commas or semicolons.
_TAG_SPLIT = re.compile(r"[,;]")


class ImportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ContactRepository(session)

    async def import_contacts_csv(
        self,
        *,
        user_id: str,
        content: bytes,
    ) -> ImportSummary:
        """Parse a CSV file and create contacts for the authenticated user.

        - Maximum CSV_ROW_LIMIT (1000) data rows; excess triggers an early-exit error.
        - Each row is validated independently; validation failures are reported as
          per-row errors without aborting the rest of the batch.
        - Tags column: comma- or semicolon-separated values, empty strings ignored.

        Returns an ImportSummary with per-row results.
        """
        text = content.decode("utf-8-sig", errors="replace")  # strip BOM if present
        reader = csv.DictReader(io.StringIO(text))

        results: list[ImportRowResult] = []
        created_count = 0
        error_count = 0

        rows = list(reader)
        if len(rows) > CSV_ROW_LIMIT:
            # Reject early — caller gets a single error entry describing the cap.
            return ImportSummary(
                total=len(rows),
                created=0,
                errors=1,
                results=[
                    ImportRowResult(
                        row=0,
                        status="error",
                        error=f"CSV exceeds the {CSV_ROW_LIMIT}-row limit ({len(rows)} rows found). "
                              "Split the file and re-upload.",
                    )
                ],
            )

        for idx, raw_row in enumerate(rows, start=1):
            row_num = idx
            try:
                # Normalise field names: strip whitespace, lowercase.
                normalised = {k.strip().lower(): (v or "").strip() for k, v in raw_row.items()}

                raw_tags = normalised.get("tags", "")
                tag_list = [t.strip() for t in _TAG_SPLIT.split(raw_tags) if t.strip()] if raw_tags else []

                import_row = ImportRow(
                    name=normalised.get("name", ""),
                    email=normalised.get("email") or None,
                    phone=normalised.get("phone") or None,
                    tags=tag_list,
                )
            except ValidationError as exc:
                first_error = exc.errors()[0]
                msg = first_error.get("msg", str(exc))
                results.append(ImportRowResult(row=row_num, status="error", error=msg))
                error_count += 1
                continue

            try:
                await self.repo.create(
                    user_id=user_id,
                    name=import_row.name,
                    email=import_row.email,
                    phone=import_row.phone,
                    # CSV import uses tag names only; tag association by ID is not
                    # supported in the import flow (tags must be created first via
                    # the /tags endpoint to obtain their IDs).
                    tag_ids=None,
                )
                results.append(ImportRowResult(row=row_num, status="created"))
                created_count += 1
            except Exception as exc:
                results.append(ImportRowResult(row=row_num, status="error", error=str(exc)))
                error_count += 1

        return ImportSummary(
            total=len(rows),
            created=created_count,
            errors=error_count,
            results=results,
        )
