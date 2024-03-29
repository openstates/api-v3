from enum import Enum
from typing import List  # , Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
from .db import SessionLocal, get_db, models
from .schemas import Event
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter

router = APIRouter()


class EventInclude(str, Enum):
    links = "links"
    sources = "sources"
    media = "media"
    documents = "documents"
    participants = "participants"
    agenda = "agenda"


class EventPagination(Pagination):
    ObjCls = Event
    IncludeEnum = EventInclude
    include_map_overrides = {
        EventInclude.links: [],
        EventInclude.sources: [],
        EventInclude.agenda: ["agenda", "agenda.related_entities", "agenda.media"],
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
    deleted: bool = Query(False, description="Return events marked as deleted?"),
    before: str = Query(
        None, description="Limit results to those starting before a given datetime."
    ),
    after: str = Query(
        None, description="Limit results to those starting before a given datetime."
    ),
    require_bills: bool = Query(
        False,
        description="Limit results to events with associated bills.",
    ),
    include: List[EventInclude] = Query(
        [], description="Additional includes for the Event response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
    pagination: EventPagination = Depends(),
):
    if not jurisdiction:
        raise HTTPException(
            400,
            "must provide 'jurisdiction' parameter",
        )
    query = (
        db.query(models.Event)
        .join(models.Event.jurisdiction)
        .outerjoin(models.Event.location)
        .filter(
            jurisdiction_filter(jurisdiction, jid_field=models.Event.jurisdiction_id),
        )
        .order_by(models.Event.start_date)
    ).options(
        contains_eager(
            models.Event.jurisdiction,
        ),
        contains_eager(
            models.Event.location,
        ),
    )

    # handle parameters
    query = query.filter(models.Event.deleted.is_(deleted))

    if before:
        query = query.filter(models.Event.start_date < before)
    if after:
        query = query.filter(models.Event.start_date > after)
    if require_bills:
        query = (
            query.outerjoin(models.Event.agenda)
            .outerjoin(models.EventAgendaItem.related_entities)
            .group_by(models.Event, models.Jurisdiction, models.EventLocation)
            .filter(models.EventRelatedEntity.entity_type == "bill")
            .having(func.count_(models.EventRelatedEntity.id) > 0)
        )

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
    query = (
        db.query(models.Event)
        .filter(models.Event.id == event_id)
        .join(models.Event.jurisdiction)
        .outerjoin(models.Event.location)
        .options(
            contains_eager(
                models.Event.jurisdiction,
            ),
            contains_eager(
                models.Event.location,
            ),
        )
    )
    return EventPagination.detail(query, includes=include)
