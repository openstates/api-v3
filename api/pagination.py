import math
from typing import List
from pydantic import create_model, BaseModel, Field
from fastapi import HTTPException
from sqlalchemy.orm import noload, selectinload
from sqlalchemy.orm.exc import NoResultFound


class PaginationMeta(BaseModel):
    per_page: int = Field(..., example=20)
    page: int = Field(..., example=1)
    max_page: int = Field(..., example=3)
    total_items: int = Field(..., example=52)


class Pagination:
    """
    Base class that handles pagination and includes= behavior together.

    Must set the following properties on subclasses:
        - ObjCls - the Pydantic model to use for the objects
        - IncludeEnum - the valid include= parameters enumeration
        - include_map_overrides - mapping of what fields to select-in if included
                        (default to same name as IncludeEnum properties)
        - postprocess_includes - function to call on each object to set includes

    Once those are set all of the basic methods work as classmethods so they can be called by
     PaginationSubclass.detail.

    The only time the class is insantiated is when it is used as a dependency for actual
    pagination.
    """

    def __init__(self, page: int = 1, per_page: int = 10):
        self.page = page
        self.per_page = per_page

    @classmethod
    def include_map(cls):
        if not hasattr(cls, "_include_map"):
            cls._include_map = {key: [key] for key in cls.IncludeEnum}
            cls._include_map.update(cls.include_map_overrides)
        return cls._include_map

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
        includes=None,
        skip_count=False,
    ):
        # shouldn't happen, but help log if it does
        if not results._order_by:
            raise HTTPException(
                status_code=500, detail="ordering is required for pagination"
            )

        if self.per_page < 1 or self.per_page > self.max_per_page:
            raise HTTPException(
                status_code=400,
                detail=f"invalid per_page, must be in [1, {self.max_per_page}]",
            )

        if not skip_count:
            total_items = results.count()
            num_pages = math.ceil(total_items / self.per_page) or 1
        else:
            # used for people.geo, always fits on one page
            total_items = 0
            num_pages = 1

        if self.page < 1 or self.page > num_pages:
            raise HTTPException(
                status_code=404, detail=f"invalid page, must be in [1, {num_pages}]"
            )

        # before the query, do the appropriate joins and noload operations
        results = self.select_or_noload(results, includes)
        results = (
            results.limit(self.per_page).offset((self.page - 1) * self.per_page).all()
        )
        results = [self.to_obj_with_includes(data, includes) for data in results]

        # make the data correct without the extra query
        if skip_count:
            total_items = len(results)

        meta = PaginationMeta(
            total_items=total_items,
            per_page=self.per_page,
            page=self.page,
            max_page=num_pages,
        )

        return {"pagination": meta, "results": results}

    @classmethod
    def detail(cls, query, *, includes):
        """ convert a single instance query to a model with the appropriate includes """
        query = cls.select_or_noload(query, includes)
        try:
            obj = query.one()
        except NoResultFound:
            raise HTTPException(
                status_code=404, detail=f"No such {cls.ObjCls.__name__}."
            )
        return cls.to_obj_with_includes(obj, includes)

    @classmethod
    def postprocess_includes(cls, obj, data, includes):
        pass

    @classmethod
    def to_obj_with_includes(cls, data, includes):
        """
        remove the non-included data from the response by setting the fields to
        None instead of [], and returning the Pydantic objects directly
        """
        newobj = cls.ObjCls.from_orm(data)
        for include in cls.IncludeEnum:
            if include not in includes:
                setattr(newobj, include, None)
        cls.postprocess_includes(newobj, data, includes)
        return newobj

    @classmethod
    def select_or_noload(cls, query, includes):
        """ either pre-join or no-load data based on whether it has been requested """
        for fieldname in cls.IncludeEnum:
            if fieldname in includes:
                # selectinload seems like a strong default choice, but it is possible that
                # some configurability might be desirable eventually for some types of data
                loader = selectinload
            else:
                loader = noload

            # update the query with appropriate loader
            for dbname in cls.include_map()[fieldname]:
                query = query.options(loader(dbname))
        return query
