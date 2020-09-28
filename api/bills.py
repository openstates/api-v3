import re
from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, cast, String, desc, nullslast
from sqlalchemy.orm import contains_eager
from .db import SessionLocal, get_db, models
from .schemas import Bill
from .pagination import Pagination
from .auth import apikey_auth
from .utils import jurisdiction_filter


class BillInclude(str, Enum):
    sponsorships = "sponsorships"
    abstracts = "abstracts"
    other_titles = "other_titles"
    other_identifiers = "other_identifiers"
    actions = "actions"
    sources = "sources"
    documents = "documents"
    versions = "versions"
    votes = "votes"


class BillSortOption(str, Enum):
    updated_desc = "updated_desc"
    first_action_asc = "first_action_asc"
    first_action_desc = "first_action_desc"
    latest_action_asc = "latest_action_asc"
    latest_action_desc = "latest_action_desc"


class BillPagination(Pagination):
    ObjCls = Bill
    IncludeEnum = BillInclude
    include_map_overrides = {
        BillInclude.sponsorships: ["sponsorships", "sponsorships.person"],
        BillInclude.versions: ["versions", "versions.links"],
        BillInclude.documents: ["documents", "documents.links"],
        BillInclude.votes: [
            "votes",
            "votes.votes",
            "votes.counts",
            "votes.sources",
            "votes.votes.voter",
        ],
    }
    max_per_page = 20


router = APIRouter()


# This code has to match openstates.transformers (TODO: combine into a package?)

_bill_id_re = re.compile(r"([A-Z]*)\s*0*([-\d]+)")
_mi_bill_id_re = re.compile(r"(SJR|HJR)\s*([A-Z]+)")
_likely_bill_id = re.compile(r"\w{1,3}\s*\d{1,5}")


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r"\1 \2", bill_id, 1).strip()
    return _bill_id_re.sub(r"\1 \2", bill_id, 1).strip()


def base_query(db):
    return (
        db.query(models.Bill)
        .join(models.Bill.legislative_session)
        .join(models.LegislativeSession.jurisdiction)
        .join(models.Bill.from_organization)
        .options(
            contains_eager(
                models.Bill.legislative_session, models.LegislativeSession.jurisdiction
            )
        )
        .options(contains_eager(models.Bill.from_organization))
    )


@router.get(
    "/bills",
    response_model=BillPagination.response_model(),
    response_model_exclude_none=True,
    tags=["bills"],
)
async def bills_search(
    jurisdiction: Optional[str] = Query(
        None, description="Filter by jurisdiction name or ID."
    ),
    session: Optional[str] = Query(None, description="Filter by session identifier."),
    chamber: Optional[str] = Query(
        None, description="Filter by chamber of origination."
    ),
    classification: Optional[str] = Query(
        None, description="Filter by classification, e.g. bill or resolution"
    ),
    subject: Optional[List[str]] = Query(
        [], description="Filter by one or more subjects."
    ),
    updated_since: Optional[str] = Query(
        None,
        description="Filter to only include bills with updates since a given date.",
    ),
    created_since: Optional[str] = Query(
        None, description="Filter to only include bills created since a given date."
    ),
    action_since: Optional[str] = Query(
        None,
        description="Filter to only include bills with an action since a given date.",
    ),
    sort: Optional[BillSortOption] = Query(
        BillSortOption.updated_desc, description="Desired sort order for bill results."
    ),
    sponsor: Optional[str] = Query(
        None,
        description="Filter to only include bills sponsored by a given name or person ID.",
    ),
    sponsor_classification: Optional[str] = Query(
        None,
        description="Filter matched sponsors to only include particular types of sponsorships.",
    ),
    q: Optional[str] = Query(None, description="Filter by full text search term."),
    include: List[BillInclude] = Query(
        [], description="Additional information to include in response."
    ),
    db: SessionLocal = Depends(get_db),
    pagination: BillPagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    """
    Search for bills matching given criteria.

    Must either specify a jurisdiction or a full text query (q).  Additional parameters will
    futher restrict bills returned.
    """
    query = base_query(db)

    if sort == BillSortOption.updated_desc:
        query = query.order_by(desc(models.Bill.updated_at))
    elif sort == BillSortOption.first_action_asc:
        query = query.order_by(nullslast(models.Bill.first_action_date))
    elif sort == BillSortOption.first_action_desc:
        query = query.order_by(nullslast(desc(models.Bill.first_action_date)))
    elif sort == BillSortOption.latest_action_asc:
        query = query.order_by(nullslast(models.Bill.latest_action_date))
    elif sort == BillSortOption.latest_action_desc:
        query = query.order_by(nullslast(desc(models.Bill.latest_action_date)))
    else:
        raise HTTPException(500, "Unknown sort option, this shouldn't happen!")

    if jurisdiction:
        query = query.filter(
            jurisdiction_filter(
                jurisdiction, jid_field=models.LegislativeSession.jurisdiction_id
            )
        )
    if session:
        if not jurisdiction:
            raise HTTPException(
                400, "filtering by session requires a jurisdiction parameter as well"
            )
        query = query.filter(models.LegislativeSession.identifier == session)
    if chamber:
        query = query.filter(models.Organization.classification == chamber)
    if classification:
        query = query.filter(models.Bill.classification.any(classification))
    if subject:
        query = query.filter(models.Bill.subject.contains(subject))
    if sponsor:
        # need to join this way, or sqlalchemy will try to join via from_organization
        query = query.join(models.Bill.sponsorships)
        if sponsor.startswith("ocd-person/"):
            query = query.filter(models.BillSponsorship.person_id == sponsor)
        else:
            query = query.filter(models.BillSponsorship.name == sponsor)
    if sponsor_classification:
        if not sponsor:
            raise HTTPException(
                400,
                "filtering by sponsor_classification requires sponsor parameter as well",
            )
        query = query.filter(
            models.BillSponsorship.classification == sponsor_classification
        )
    if updated_since:
        query = query.filter(cast(models.Bill.updated_at, String) >= updated_since)
    if created_since:
        query = query.filter(cast(models.Bill.created_at, String) >= created_since)
    if action_since:
        query = query.filter(models.Bill.latest_action_date >= action_since)
    if q:
        if _likely_bill_id.match(q):
            query = query.filter(
                func.upper(models.Bill.identifier) == fix_bill_id(q).upper()
            )
        else:
            query = query.join(models.SearchableBill).filter(
                models.SearchableBill.search_vector.op("@@")(
                    func.websearch_to_tsquery(q, config="english")
                )
            )

    if not q and not jurisdiction:
        raise HTTPException(400, "either 'jurisdiction' or 'q' required")

    # handle includes

    resp = pagination.paginate(query, includes=include)

    return resp


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/bills/ocd-bill/{openstates_bill_id}",
    response_model=Bill,
    response_model_exclude_none=True,
    tags=["bills"],
)
async def bill_detail_by_id(
    openstates_bill_id: str,
    include: List[BillInclude] = Query([]),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """ Obtain bill information by internal ID in the format ocd-bill/*uuid*. """
    query = base_query(db).filter(models.Bill.id == "ocd-bill/" + openstates_bill_id)
    return BillPagination.detail(query, includes=include)


@router.get(
    # we have to use the Starlette path type to allow slashes here
    "/bills/{jurisdiction}/{session}/{bill_id}",
    response_model=Bill,
    response_model_exclude_none=True,
    tags=["bills"],
)
async def bill_detail(
    jurisdiction: str,
    session: str,
    bill_id: str,
    include: List[BillInclude] = Query([]),
    db: SessionLocal = Depends(get_db),
    auth: str = Depends(apikey_auth),
):
    """ Obtain bill information based on (state, session, bill_id)."""
    query = base_query(db).filter(
        models.Bill.identifier == fix_bill_id(bill_id).upper(),
        models.LegislativeSession.identifier == session,
        jurisdiction_filter(
            jurisdiction, jid_field=models.LegislativeSession.jurisdiction_id
        ),
    )
    return BillPagination.detail(query, includes=include)
