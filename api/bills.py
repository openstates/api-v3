from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException

# from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Bill
from .pagination import Pagination
from .auth import apikey_auth

# from .utils import joined_or_noload


class BillSegment(str, Enum):
    sponsorships = "sponsorships"


router = APIRouter()


def jurisdiction_filter(j):
    if len(j) == 2:
        try:
            return (
                models.LegislativeSession.jurisdiction_id
                == lookup(abbr=j).jurisdiction_id
            )
        except KeyError:
            return models.Jurisdiction.name == j
    elif j.startswith("ocd-jurisdiction"):
        return models.LegislativeSession.jurisdiction_id == j
    else:
        return models.Jurisdiction.name == j


@router.get(
    "/bills", response_model=Pagination.of(Bill), response_model_exclude_none=True
)
async def bills(
    jurisdiction: Optional[str] = None,
    session: Optional[str] = None,
    chamber: Optional[str] = None,
    classification: Optional[str] = None,
    subject: Optional[str] = None,
    updated_since: Optional[str] = None,
    action_since: Optional[str] = None,
    # sponsor
    # q
    segments: List[BillSegment] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: Pagination = Depends(Pagination),
    auth: str = Depends(apikey_auth),
):
    query = (
        db.query(models.Bill)
        .join(models.Bill.legislative_session)
        .join(models.Bill.from_organization)
        .order_by(models.LegislativeSession.identifier, models.Bill.identifier)
        .options(contains_eager(models.Bill.legislative_session))
        # .options(contains_eager(models.Bill.legislative_session.jurisdiction))
    )
    filtered = False

    if jurisdiction:
        query = query.filter(jurisdiction_filter(jurisdiction))
        filtered = True
    if session:
        query = query.filter(models.LegislativeSession.identifier == session)
    if chamber:
        query = query.filter(models.Organization.classification == chamber)
    if classification:
        query = query.filter(models.Bill.classification.any(classification))
    if subject:
        query = query.filter(models.Bill.subject.any(subject))
    if updated_since:
        query = query.filter(models.Bill.updated_at > updated_since)
    if action_since:
        query = query.filter(models.Bill.latest_action_date > action_since)

    if not filtered:
        raise HTTPException(400, "either 'jurisdiction' or 'q' required")

    # TODO: handle segments
    # query = joined_or_noload(query, PersonSegment.other_names, segments)

    resp = pagination.paginate(query)

    resp["results"] = [Bill.with_segments(r, segments) for r in resp["results"]]

    return resp
