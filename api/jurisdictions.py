from enum import Enum
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from .db import SessionLocal, get_db, models
from .schemas import Jurisdiction, JurisdictionClassification
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter


class JurisdictionInclude(str, Enum):
    organizations = "organizations"
    legislative_sessions = "legislative_sessions"
    latest_runs = "latest_runs"


class JurisdictionPagination(Pagination):
    ObjCls = Jurisdiction
    IncludeEnum = JurisdictionInclude
    include_map_overrides = {
        JurisdictionInclude.organizations: ["organizations", "organizations.posts"],
        JurisdictionInclude.latest_runs: [],  # no preloading for this one, needs to be dynamic
    }
    max_per_page = 52

    @classmethod
    def postprocess_includes(cls, obj, data, includes):
        # latest runs needs to be set on each object individually, the 20-item
        # limit makes a subquery approach not work
        if JurisdictionInclude.latest_runs in includes:
            obj.latest_runs = data.get_latest_runs()

    def __init__(self, page: int = 1, per_page: int = 52):
        self.page = page
        self.per_page = per_page


router = APIRouter()


@router.get(
    "/jurisdictions",
    response_model=JurisdictionPagination.response_model(),
    response_model_exclude_none=True,
    tags=["jurisdictions"],
)
async def jurisdiction_list(
    classification: Optional[JurisdictionClassification] = Query(
        None, description="Filter returned jurisdictions by type."
    ),
    include: List[JurisdictionInclude] = Query(
        [], description="Additional information to include in response."
    ),
    db: SessionLocal = Depends(get_db),
    pagination: JurisdictionPagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    """
    Get list of supported Jurisdictions, a Jurisdiction is a state or municipality.
    """
    query = db.query(models.Jurisdiction).order_by(models.Jurisdiction.name)

    # handle parameters
    if classification:
        query = query.filter(models.Jurisdiction.classification == classification)

    return pagination.paginate(query, includes=include)


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/jurisdictions/{jurisdiction_id:path}",
    response_model=Jurisdiction,
    response_model_exclude_none=True,
    tags=["jurisdictions"],
)
async def jurisdiction_detail(
    jurisdiction_id: str,
    include: List[JurisdictionInclude] = Query(
        [], description="Additional includes for the Jurisdiction response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """Get details on a single Jurisdiction (e.g. state or municipality)."""
    query = db.query(models.Jurisdiction).filter(
        jurisdiction_filter(jurisdiction_id, jid_field=models.Jurisdiction.id)
    )
    return JurisdictionPagination.detail(query, includes=include)
