from enum import Enum
from typing import List
from fastapi import APIRouter, Depends, Query
from .db import SessionLocal, get_db, models
from .schemas import Committee
from .pagination import Pagination
from .auth import apikey_auth


router = APIRouter()


class CommitteeInclude(str, Enum):
    memberships = "memberships"


class CommitteePagination(Pagination):
    ObjCls = Committee
    IncludeEnum = CommitteeInclude
    include_map_overrides = {
        CommitteeInclude.memberships: [],
    }
    max_per_page = 20

    # @classmethod
    # def postprocess_includes(cls, obj, data, includes):
    #     pass

    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = page
        self.per_page = per_page


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/committees/{committee_id:path}",
    response_model=Committee,
    response_model_exclude_none=True,
    tags=["committees"],
)
async def committee_detail(
    committee_id: str,
    include: List[CommitteeInclude] = Query(
        [], description="Additional includes for the Committee response."
    ),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """ Get details on a single committee by ID. """
    print(committee_id)
    query = db.query(models.Organization).filter(
        models.Organization.id == committee_id,
        models.Organization.classification.in_(("committee", "subcommittee")),
    )
    return CommitteePagination.detail(query, includes=include)
