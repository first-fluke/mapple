"""Imports router — bulk CSV contact import.

POST /imports/contacts
  - Accepts multipart/form-data with a single CSV file field named "file".
  - Columns: name, email, phone, tags  (tags = comma- or semicolon-separated).
  - Cap: 1 000 rows per upload.
  - Response: per-row result report {row, status: created|error, error?}.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.imports.schemas import ImportSummary
from src.imports.service import ImportService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import AppException
from src.lib.rate_limit import check_data_rate_limit

router = APIRouter(prefix="/imports", tags=["imports"], dependencies=[Depends(check_data_rate_limit)])

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB safety cap


@router.post("/contacts", status_code=200)
async def import_contacts_csv(
    file: UploadFile = File(..., description="CSV file with columns: name, email, phone, tags"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ImportSummary:
    """Import contacts from a CSV file.

    Each row is processed independently — validation errors on individual rows
    are reported in the response without aborting the rest of the batch.
    Rows beyond the 1 000-row cap cause an immediate rejection with a clear message.
    """
    if file.content_type and "csv" not in file.content_type and "text" not in file.content_type:
        raise AppException(
            status_code=422,
            code="INVALID_FILE_TYPE",
            message=f"Expected a CSV file, got content-type: {file.content_type}",
        )

    content = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(content) > _MAX_UPLOAD_BYTES:
        raise AppException(
            status_code=413,
            code="FILE_TOO_LARGE",
            message=f"CSV file must be smaller than {_MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
        )

    service = ImportService(session)
    return await service.import_contacts_csv(user_id=user_id, content=content)
