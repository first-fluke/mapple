from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.auth import get_current_user_id
from src.lib.database import get_session
from src.lib.exceptions import ApiResponse
from src.organizations.schemas import OrganizationCreate, OrganizationOut
from src.organizations.service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("")
async def search_organizations(
    q: str = Query(default="", max_length=255),
    _user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[OrganizationOut]]:
    """Autocomplete search for organizations by name (ILIKE, top 10)."""
    service = OrganizationService(session)
    orgs = await service.search(q)
    return ApiResponse(data=[OrganizationOut.model_validate(o) for o in orgs])


@router.post("", status_code=201)
async def create_organization(
    body: OrganizationCreate,
    _user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OrganizationOut]:
    """Create an organization with name+type dedup."""
    service = OrganizationService(session)
    org = await service.create(name=body.name, org_type=body.type)
    return ApiResponse(data=OrganizationOut.model_validate(org))
