from enum import Enum
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import joinedload, noload
from .db import SessionLocal, get_db, models
from .schemas import Jurisdiction, JurisdictionEnum
from .pagination import Pagination



class JurisdictionSegment(str, Enum):
    organizations = "organizations"


router = APIRouter()


@router.get(
    "/jurisdictions",
    response_model=Pagination.of(Jurisdiction),
    response_model_exclude_unset=True,
)
async def jurisdictions(
    classification: Optional[JurisdictionEnum] = None,
    segments: List[JurisdictionSegment] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: dict = Depends(Pagination),
):
    # TODO: remove this conversion once database is updated
    if classification == "state":
        classification = "government"
    query = db.query(models.Jurisdiction).order_by(models.Jurisdiction.name)

    # handle segments
    if JurisdictionSegment.organizations in segments:
        query = query.options(joinedload(models.Jurisdiction.organizations))
    else:
        query = query.options(noload(models.Jurisdiction.organizations))

    # handle parameters
    if classification:
        query = query.filter(models.Jurisdiction.classification == classification)
    resp = pagination.paginate(query)

    # TODO: this should be removed too (see above note)
    for result in resp["results"]:
        if result.classification == "government":
            result.classification = "state"
    resp["results"] = [Jurisdiction.with_segments(r, segments) for r in resp["results"]]

    return resp
