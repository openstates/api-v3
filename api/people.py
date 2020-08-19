from typing import Optional
from enum import Enum
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import joinedload, noload
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Person
from .pagination import Pagination


class PersonSegment(str, Enum):
    pass


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
    db: SessionLocal = Depends(get_db),
    pagination: dict = Depends(Pagination),
):
    query = db.query(models.Person).order_by(models.Person.name)

    query = query.filter(
        jurisdiction_filter(jurisdiction),
        models.Person.current_role.isnot(None),     # current members only for now
    ).join(models.Jurisdiction)
    resp = pagination.paginate(query)

    return resp
