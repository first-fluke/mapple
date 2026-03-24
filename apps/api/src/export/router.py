from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.export.service import ExportService
from src.lib.auth import get_current_user_id
from src.lib.database import get_session

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/contacts")
async def export_contacts(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """Export contacts with experiences as CSV."""
    service = ExportService(session)
    csv_content = await service.export_contacts_csv(user_id)

    return StreamingResponse(
        content=iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"},
    )
