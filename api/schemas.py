from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class SegmentableBase(BaseModel):
    @classmethod
    def with_segments(Cls, obj, segments):
        newobj = Cls.from_orm(obj)
        for segment, fields in Cls.__config__.segments.items():
            if segment not in segments:
                for field in fields:
                    setattr(newobj, field, None)
        return newobj


class PaginationMeta(BaseModel):
    per_page: int
    page: int
    max_page: int
    total_items: int


class JurisdictionEnum(str, Enum):
    state = "state"
    municipality = "municipality"


class JurisdictionSegment(str, Enum):
    organizations = "organizations"


class Organization(BaseModel):
    id: str
    name: str
    classification: str

    class Config:
        orm_mode = True


class Jurisdiction(SegmentableBase):
    id: str
    name: str
    classification: JurisdictionEnum
    division_id: Optional[str] = ""  # never exclude
    url: str
    # TODO: add these
    # people_last_updated: Optional[datetime.datetime]
    # bills_last_updated: Optional[datetime.datetime]
    organizations: Optional[List[Organization]] = None

    class Config:
        orm_mode = True
        segments = {
            "organizations": ["organizations"]
        }


class Person(BaseModel):
    id: str
    name: str
