from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Person, OrgClassification
from .pagination import Pagination
from .auth import apikey_auth
from .utils import joined_or_noload


class PersonInclude(str, Enum):
    other_names = "other_names"
    other_identifiers = "other_identifiers"
    links = "links"
    sources = "sources"
    offices = "offices"


class PeoplePagination(Pagination):
    ObjCls = Person
    IncludeEnum = PersonInclude


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
    "/people",
    response_model=PeoplePagination.response_model(),
    response_model_exclude_none=True,
)
async def people(
    jurisdiction: Optional[str] = None,
    name: Optional[str] = None,
    id: Optional[List[str]] = Query([]),
    org_classification: Optional[OrgClassification] = None,
    include: List[PersonInclude] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: PeoplePagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    query = (
        db.query(models.Person)
        .join(models.Person.jurisdiction)
        .order_by(models.Person.name)
        .options(contains_eager(models.Person.jurisdiction))
    )
    filtered = False

    if jurisdiction:
        query = query.filter(
            jurisdiction_filter(jurisdiction),
            models.Person.current_role.isnot(None),  # current members only for now
        )
        filtered = True
    if name:
        lname = name.lower()
        query = query.filter(
            or_(
                func.lower(models.Person.name) == lname,
                func.lower(models.PersonName.name) == lname,
            )
        ).outerjoin(models.PersonName)
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

    # handle includes
    query = joined_or_noload(query, PersonInclude.other_names, include)
    query = joined_or_noload(query, PersonInclude.other_identifiers, include)
    query = joined_or_noload(query, PersonInclude.links, include)
    query = joined_or_noload(query, PersonInclude.sources, include)
    query = joined_or_noload(
        query, PersonInclude.offices, include, dbname="contact_details"
    )

    resp = pagination.paginate(query, includes=include)

    return resp
