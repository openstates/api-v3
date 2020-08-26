from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query  # , HTTPException

# from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager
from .db import SessionLocal, get_db, models
from .schemas import Bill
from .pagination import Pagination
from .auth import apikey_auth

# from .utils import joined_or_noload


class BillSegment(str, Enum):
    sponsorships = "sponsorships"


router = APIRouter()


@router.get(
    "/bills", response_model=Pagination.of(Bill), response_model_exclude_none=True
)
async def bills(
    jurisdiction: Optional[str] = None,
    id: Optional[List[str]] = Query([]),
    segments: List[BillSegment] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    auth: str = Depends(apikey_auth),
):
    query = (
        db.query(models.Bill)
        .join(models.Bill.legislative_session)
        .order_by(models.Bill.identifier)
        .options(contains_eager(models.Bill.legislative_session))
    )
    # filtered = False

    # if not filtered:
    #     raise HTTPException(400, "either 'jurisdiction', 'name', or 'id' is required")

    # handle segments
    # query = joined_or_noload(query, PersonSegment.other_names, segments)

    resp = pagination.paginate(query)

    resp["results"] = [Bill.with_segments(r, segments) for r in resp["results"]]

    return resp
