from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager
from .db import SessionLocal, get_db, models
from .schemas import Person, OrgClassification
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter


class PersonInclude(str, Enum):
    other_names = "other_names"
    other_identifiers = "other_identifiers"
    links = "links"
    sources = "sources"
    offices = "offices"


class PeoplePagination(Pagination):
    ObjCls = Person
    IncludeEnum = PersonInclude
    include_map_overrides = {PersonInclude.offices: ["contact_details"]}


router = APIRouter()


@router.get(
    "/people",
    response_model=PeoplePagination.response_model(),
    response_model_exclude_none=True,
)
async def people_search(
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
            jurisdiction_filter(jurisdiction, jid_field=models.Person.jurisdiction_id),
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

    resp = pagination.paginate(query, includes=include)

    return resp
