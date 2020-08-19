from typing import Optional
from enum import Enum
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import joinedload, noload
from .db import SessionLocal, get_db, models
from .schemas import Person
from .pagination import Pagination


class PersonSegment(str, Enum):
    pass


router = APIRouter()


@router.get(
    "/people",
    response_model=Pagination.of(Person),
    response_model_exclude_none=True,
)
async def people(
    jurisdiction: str,
    chamber: Optional[str] = None,
    name: Optional[str] = None,
    db: SessionLocal = Depends(get_db),
    pagination: dict = Depends(Pagination),
):
    query = db.query(models.Person).order_by(models.Person.name)

    query = query.filter(models.Person.jurisdiction_id == jurisdiction, models.Person.current_role != None)
    resp = pagination.paginate(query)

    return resp
