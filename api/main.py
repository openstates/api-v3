from typing import Optional, List
import math
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import create_model
from sqlalchemy.orm import joinedload, noload
from .db import SessionLocal, models
from .schemas import PaginationMeta, JurisdictionEnum, Jurisdiction, JurisdictionSegment


# dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Pagination:
    def __init__(self, page: int = 1, per_page: int = 100):
        self.page = page
        self.per_page = per_page

    @staticmethod
    def of(Cls):
        # dynamically define a new class that is just results & pagination
        # this will only be dynamically constructed at start so the cost is negligible
        return create_model(
            f"{Cls.__name__}List",
            results=(List[Cls], ...),
            pagination=(PaginationMeta, ...),
        )

    def paginate(self, results, max_per_page=100):
        # shouldn't happen, but help log if it does
        if not results._order_by:
            raise HTTPException(
                status_code=500, detail="ordering is required for pagination"
            )

        if self.per_page < 1 or self.per_page > max_per_page:
            raise HTTPException(
                status_code=400,
                detail=f"invalid per_page, must be in [1, {max_per_page}]",
            )

        total_items = results.count()
        num_pages = math.ceil(total_items / self.per_page)

        if self.page < 1 or self.page > num_pages:
            raise HTTPException(
                status_code=404, detail=f"no such page, must be in [1, {num_pages}]"
            )

        meta = PaginationMeta(
            total_items=total_items,
            per_page=self.per_page,
            page=self.page,
            max_page=num_pages,
        )
        return {
            "pagination": meta,
            "results": results.limit(self.per_page)
            .offset((self.page - 1) * self.per_page)
            .all(),
        }


app = FastAPI()


@app.get(
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
