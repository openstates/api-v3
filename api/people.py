from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Person, OrgClassification
from .pagination import Pagination
from .auth import apikey_auth
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
    jurisdiction: Optional[str] = None,
    name: Optional[str] = None,
    id: Optional[List[str]] = Query([]),
    org_classification: Optional[OrgClassification] = None,
    segments: List[PersonSegment] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    auth: str = Depends(apikey_auth),
):
    query = (
        db.query(models.Person).join(models.Jurisdiction).order_by(models.Person.name)
    )
    filtered = False

    if jurisdiction:
        query = query.filter(
            jurisdiction_filter(jurisdiction),
            models.Person.current_role.isnot(None),  # current members only for now
        )
        filtered = True
    if name:
        query = query.filter(func.lower(models.Person.name) == name.lower())
        filtered = True
    if id:
        query = query.filter(models.Person.id.in_(id))
        filtered = True
    if org_classification:
        query = query.filter(
            models.Person.current_role["org_classification"].astext
            == org_classification
        )

    if not filtered:
        raise HTTPException(400, "either 'jurisdiction', 'name', or 'id' is required")

    # handle segments
    query = joined_or_noload(query, PersonSegment.other_names, segments)
    query = joined_or_noload(query, PersonSegment.other_identifiers, segments)
    query = joined_or_noload(query, PersonSegment.links, segments)
    query = joined_or_noload(query, PersonSegment.sources, segments)
    query = joined_or_noload(
        query, PersonSegment.offices, segments, dbname="contact_details"
    )

    resp = pagination.paginate(query)

    resp["results"] = [Person.with_segments(r, segments) for r in resp["results"]]

    return resp
