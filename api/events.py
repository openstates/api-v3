from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from .db import SessionLocal, get_db, models
from .schemas import Event, OrgClassification # , EventClassification
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter

router = APIRouter()


class EventInclude(str, Enum):
    # memberships = "memberships"
    links = "links"
    sources = "sources"


class EventPagination(Pagination):
    ObjCls = Event
    IncludeEnum = EventInclude
    include_map_overrides = {
        # EventInclude.memberships: ["memberships", "memberships.person"],
        EventInclude.links: [],
        EventInclude.sources: [],
    }
    max_per_page = 20

    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = page
        self.per_page = per_page


@router.get(
    "/events",
    response_model=EventPagination.response_model(),
    response_model_exclude_none=True,
    tags=["events"],
)
async def event_list(
    jurisdiction: str = Query(None, description="Filter by jurisdiction name or ID."),
    classification: Optional[EventClassification] = None,
    # parent: Optional[str] = Query(
    #     None, description="ocd-organization ID of parent event."
    # ),
    # chamber: Optional[OrgClassification] = Query(
    #     None, description="Chamber of event, generally upper or lower."
    # ),
    include: List[EventInclude] = Query(
        [], description="Additional includes for the Event response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
    pagination: EventPagination = Depends(),
):
    query = (
        db.query(models.Organization)
        .filter(
            models.Organization.classification.in_("event"),
            jurisdiction_filter(
                jurisdiction, jid_field=models.Organization.jurisdiction_id
            ),
        )
        .order_by(models.Organization.name)
    )

    # handle parameters
    if classification:
        query = query.filter(models.Organization.classification == classification)
    # if parent:
    #     query = query.filter(models.Organization.parent_id == parent)
    # if chamber:
    #     subquery = (
    #         db.query(models.Organization.id)
    #         .filter(
    #             models.Organization.classification == chamber,
    #             jurisdiction_filter(
    #                 jurisdiction, jid_field=models.Organization.jurisdiction_id
    #             ),
    #         )
    #         .scalar_subquery()
    #     )
    #     query = query.filter(models.Organization.parent_id == subquery)

    return pagination.paginate(query, includes=include)


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/events/{event_id:path}",
    response_model=Event,
    response_model_exclude_none=True,
    tags=["events"],
)
async def event_detail(
    event_id: str,
    include: List[EventInclude] = Query(
        [], description="Additional includes for the Event response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """Get details on a single event by ID."""
    query = db.query(models.Organization).filter(
        models.Organization.id == event_id,
        models.Organization.classification.in_("event"),
    )
    return EventPagination.detail(query, includes=include)