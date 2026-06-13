from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EdgeType(StrEnum):
    COMPANY = "company"
    SCHOOL = "school"
    TAG = "tag"
    REGION = "region"
    MEETING = "meeting"


class EdgeOut(BaseModel):
    source_contact_id: int
    target_contact_id: int
    type: EdgeType
    label: str


class ClusterOut(BaseModel):
    id: int
    type: EdgeType
    label: str
    contact_ids: list[int]


# ---------------------------------------------------------------------------
# Force-graph data shapes — must match web GraphResponse exactly.
#
# avatarUrl is the only camelCase key the web type expects. We use
# serialization_alias so that FastAPI's JSON output emits "avatarUrl" while
# the Python attribute stays snake_case (avatar_url). populate_by_name=True
# allows constructing with avatar_url= keyword.
# ---------------------------------------------------------------------------


class LinkType(StrEnum):
    """Web LinkType enum values (colleague | classmate | friend | other).

    Mapping from organization type:
    - 'company' org shared between contacts → 'colleague'
    - 'school'  org shared between contacts → 'classmate'
    - no shared org found                   → 'friend'
    - any other org type                    → 'other'
    """

    COLLEAGUE = "colleague"
    CLASSMATE = "classmate"
    FRIEND = "friend"
    OTHER = "other"


class GraphNodeOut(BaseModel):
    """Single node in the force-graph; maps to web GraphNode."""

    model_config = ConfigDict(
        populate_by_name=True,
        # Emit serialization aliases in JSON output so FastAPI returns camelCase.
        serialize_by_alias=True,
    )

    id: str
    name: str
    # serialization_alias emits "avatarUrl" in JSON; populate_by_name lets us
    # construct with avatar_url= directly.
    avatar_url: str | None = Field(default=None, serialization_alias="avatarUrl")


class GraphLinkOut(BaseModel):
    """Single directed edge in the force-graph; maps to web GraphLink."""

    source: str
    target: str
    type: LinkType
    label: str | None = None


class GraphDataOut(BaseModel):
    """Top-level response body; matches web GraphResponse."""

    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
    )

    nodes: list[GraphNodeOut]
    links: list[GraphLinkOut]
