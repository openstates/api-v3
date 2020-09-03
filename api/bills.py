import re
from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, cast, String
from sqlalchemy.orm import contains_eager
from openstates_metadata import lookup
from .db import SessionLocal, get_db, models
from .schemas import Bill
from .pagination import Pagination
from .auth import apikey_auth
from .utils import joined_or_noload


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


class BillPagination(Pagination):
    ObjCls = Bill
    IncludeEnum = BillInclude


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


# This code has to match openstates.transformers (TODO: combine into a package?)

_bill_id_re = re.compile(r"([A-Z]*)\s*0*([-\d]+)")
_mi_bill_id_re = re.compile(r"(SJR|HJR)\s*([A-Z]+)")
_likely_bill_id = re.compile(r"\w{1,3}\s*\d{1,5}")


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r"\1 \2", bill_id, 1).strip()
    return _bill_id_re.sub(r"\1 \2", bill_id, 1).strip()


@router.get(
    "/bills",
    response_model=BillPagination.response_model(),
    response_model_exclude_none=True,
)
async def bills(
    jurisdiction: Optional[str] = None,
    session: Optional[str] = None,
    chamber: Optional[str] = None,
    classification: Optional[str] = None,
    subject: Optional[List[str]] = Query([]),
    updated_since: Optional[str] = None,
    action_since: Optional[str] = None,
    # TODO: sponsor: Optional[str] = None,
    q: Optional[str] = None,
    include: List[BillInclude] = Query([]),
    db: SessionLocal = Depends(get_db),
    pagination: BillPagination = Depends(),
    auth: str = Depends(apikey_auth),
):
    query = (
        db.query(models.Bill)
        .join(models.Bill.legislative_session)
        .join(models.LegislativeSession.jurisdiction)
        .join(models.Bill.from_organization)
        .order_by(models.LegislativeSession.identifier, models.Bill.identifier)
        .options(
            contains_eager(
                models.Bill.legislative_session, models.LegislativeSession.jurisdiction
            )
        )
        .options(contains_eager(models.Bill.from_organization))
    )

    if jurisdiction:
        query = query.filter(jurisdiction_filter(jurisdiction))
    if session:
        query = query.filter(models.LegislativeSession.identifier == session)
    if chamber:
        query = query.filter(models.Organization.classification == chamber)
    if classification:
        query = query.filter(models.Bill.classification.any(classification))
    if subject:
        query = query.filter(models.Bill.subject.contains(subject))
    if updated_since:
        query = query.filter(cast(models.Bill.updated_at, String) >= updated_since)
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
    for segval in BillInclude:
        query = joined_or_noload(query, segval, include)
    query = joined_or_noload(
        query, BillInclude.versions, include, dbname="versions.links"
    )
    query = joined_or_noload(
        query, BillInclude.documents, include, dbname="documents.links"
    )
    query = joined_or_noload(query, BillInclude.votes, include, dbname="votes.votes")
    query = joined_or_noload(query, BillInclude.votes, include, dbname="votes.counts")
    query = joined_or_noload(query, BillInclude.votes, include, dbname="votes.sources")

    resp = pagination.paginate(query, includes=include)

    return resp
