import math
from typing import List
from pydantic import create_model, BaseModel
from fastapi import HTTPException


class PaginationMeta(BaseModel):
    per_page: int
    page: int
    max_page: int
    total_items: int


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
        num_pages = math.ceil(total_items / self.per_page) or 1

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
