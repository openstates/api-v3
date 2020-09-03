import math
from typing import List
from pydantic import create_model, BaseModel
from fastapi import HTTPException
from sqlalchemy.orm import noload, selectinload


class PaginationMeta(BaseModel):
    per_page: int
    page: int
    max_page: int
    total_items: int


class Pagination:
    """
    Must set the following properties on subclasses:
        - ObjCls - the Pydantic model to use for the objects
        - IncludeEnum - the valid include= parameters enumeration
        - include_map_overrides - mapping of what fields to select-in if included
                        (default to same name as IncludeEnum properties)
    """

    def __init__(self, page: int = 1, per_page: int = 100):
        self.page = page
        self.per_page = per_page

        self.include_map = {key: [key] for key in self.IncludeEnum}
        self.include_map.update(self.include_map_overrides)

    @classmethod
    def response_model(cls):
        return create_model(
            f"{cls.ObjCls.__name__}List",
            results=(List[cls.ObjCls], ...),
            pagination=(PaginationMeta, ...),
        )

    def paginate(
        self,
        results,
        *,
        max_per_page=100,
        cls=None,
        includes=None,
        available_includes=None,
    ):
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
                status_code=404, detail=f"invalid page, must be in [1, {num_pages}]"
            )

        meta = PaginationMeta(
            total_items=total_items,
            per_page=self.per_page,
            page=self.page,
            max_page=num_pages,
        )

        # before the query, do the appropriate joins and noload operations
        results = self.select_or_noload(results, includes)
        results = (
            results.limit(self.per_page).offset((self.page - 1) * self.per_page).all()
        )
        results = [self.to_obj_with_includes(data, includes) for data in results]
        return {"pagination": meta, "results": results}

    def to_obj_with_includes(self, data, includes):
        # remove the non-included data from the response by setting the fields to
        # None instead of [], and returning the Pydantic objects directly
        newobj = self.ObjCls.from_orm(data)
        for include in self.IncludeEnum:
            if include not in includes:
                setattr(newobj, include, None)
        return newobj

    def select_or_noload(self, query, includes):
        """ either pre-join or no-load data based on whether it has been requested """
        for fieldname in self.IncludeEnum:
            if fieldname in includes:
                # selectinload seems like a strong default choice, but it is possible that
                # some configurability might be desirable eventually for some types of data
                loader = selectinload
            else:
                loader = noload

            # update the query with appropriate loader
            for dbname in self.include_map[fieldname]:
                query = query.options(loader(dbname))
        return query
