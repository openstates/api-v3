from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Person
from .pagination import Pagination
from .utils import joined_or_noload


class PersonSegment(str, Enum):
    other_names = "other_names"
    other_identifiers = "other_identifiers"
    links = "links"
    sources = "sources"
    offices = "offices"


router = APIRouter()


def jurisdiction_filter(j):
    if len(j) == 2:
        try:
            return models.Person.jurisdiction_id == lookup(abbr=j).jurisdiction_id
        except KeyError:
            return models.Jurisdiction.name == j
    elif j.startswith("ocd-jurisdiction"):
        return models.Person.jurisdiction_id == j
    else:
        return models.Jurisdiction.name == j


@router.get(
    "/people", response_model=Pagination.of(Person), response_model_exclude_none=True
)
async def people(
    jurisdiction: str,
    chamber: Optional[str] = None,
    name: Optional[str] = None,
    segments: List[PersonSegment] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: dict = Depends(Pagination),
):
    query = db.query(models.Person).order_by(models.Person.name)

    query = query.filter(
        jurisdiction_filter(jurisdiction),
        models.Person.current_role.isnot(None),  # current members only for now
    ).join(models.Jurisdiction)

    # handle segments
    query = joined_or_noload(query, PersonSegment.other_names, segments)
    query = joined_or_noload(query, PersonSegment.other_identifiers, segments)
    query = joined_or_noload(query, PersonSegment.links, segments)
    query = joined_or_noload(query, PersonSegment.sources, segments)
    query = joined_or_noload(query, PersonSegment.offices, segments, dbname="contact_details")

    resp = pagination.paginate(query)

    resp["results"] = [Person.with_segments(r, segments) for r in resp["results"]]

    return resp
