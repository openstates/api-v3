from typing import Optional, List
from enum import Enum
import requests
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager
from .db import SessionLocal, get_db, models
from .schemas import Person, OrgClassification
from .pagination import Pagination, PaginationMeta
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
    include_map_overrides = {}
    max_per_page = 50


# have to save this here since generating it twice caused a FastAPI error
PersonList = PeoplePagination.response_model()


def people_query(db):
    return (
        db.query(models.Person)
        .join(models.Person.jurisdiction)
        .order_by(models.Person.name)
        .options(contains_eager(models.Person.jurisdiction))
    )


router = APIRouter()


@router.get(
    "/people",
    response_model=PersonList,
    response_model_exclude_none=True,
    tags=["people"],
)
async def people_search(
    jurisdiction: Optional[str] = Query(
        None, description="Filter by jurisdiction name or id."
    ),
    name: Optional[str] = Query(
        None, description="Filter by name, case-insensitive match."
    ),
    id: Optional[List[str]] = Query(
        [],
        description="Filter by id, can be specified multiple times for multiple people.",
    ),
    org_classification: Optional[OrgClassification] = Query(
        None, description="Filter by current role."
    ),
    district: Optional[str] = Query(
        None,
        description="Filter by district name.",
    ),
    include: List[PersonInclude] = Query(
        [], description="Additional information to include in response."
    ),
    db: SessionLocal = Depends(get_db),
    pagination: PeoplePagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    """
    Get list of people matching selected criteria.

    Must provide either **jurisdiction**, **name**, or one or more **id** parameters.
    """

    query = people_query(db)
    filtered = False

    if jurisdiction:
        query = query.filter(
            jurisdiction_filter(jurisdiction, jid_field=models.Person.jurisdiction_id),
            models.Person.current_role.isnot(None),  # current members only for now
        )
        filtered = True
    if name:
        lname = f"%{name.lower()}%"
        query = query.filter(
            or_(
                func.lower(models.Person.name).like(lname),
                func.lower(models.PersonName.name).like(lname),
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
    if district:
        if not jurisdiction:
            raise HTTPException(400, "cannot specify 'district' without 'jurisdiction'")
        query = query.filter(models.Person.current_role["district"].astext == district)

    if not filtered:
        raise HTTPException(400, "either 'jurisdiction', 'name', or 'id' is required")

    return pagination.paginate(query, includes=include)


@router.get(
    "/people.geo",
    response_model=PersonList,
    response_model_exclude_none=True,
    tags=["people"],
)
async def people_geo(
    lat: float = Query(..., description="Latitude of point."),
    lng: float = Query(..., description="Longitude of point."),
    include: List[PersonInclude] = Query(
        [], description="Additional information to include in the response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """
    Get list of people currently representing a given location.

    **Note:** Currently limited to state legislators.  Governors & mayors are not included.
    """
    url = f"https://v3.openstates.org/divisions.geo?lat={lat}&lng={lng}"
    data = requests.get(url).json()
    try:
        divisions = [d["id"] for d in data["divisions"]]
    except KeyError:
        raise HTTPException(
            500, "unexpected upstream response, try again in 60 seconds"
        )

    # skip the rest of the logic if there are no divisions
    if not divisions:
        return {
            "pagination": PaginationMeta(
                total_items=0, per_page=100, page=1, max_page=1
            ),
            "results": [],
        }

    query = people_query(db).filter(
        models.Person.current_role["division_id"].astext.in_(divisions)
    )
    # paginate without looking for page= params
    pagination = PeoplePagination()
    return pagination.paginate(query, includes=include, skip_count=True)
