import datetime
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field


class SegmentableBase(BaseModel):
    @classmethod
    def with_segments(Cls, obj, segments):
        newobj = Cls.from_orm(obj)
        for segment, fields in Cls.__config__.segments.items():
            if segment not in segments:
                for field in fields:
                    setattr(newobj, field, None)
        return newobj


class JurisdictionClassification(str, Enum):
    state = "state"
    municipality = "municipality"


class OrgClassification(str, Enum):
    legislature = "legislature"
    executive = "executive"
    lower = "lower"
    upper = "upper"


class Organization(BaseModel):
    id: str
    name: str
    classification: str

    class Config:
        orm_mode = True


class Jurisdiction(SegmentableBase):
    id: str
    name: str
    classification: JurisdictionClassification
    division_id: Optional[str] = ""  # never exclude
    url: str
    # TODO: add these
    # people_last_updated: Optional[datetime.datetime]
    # bills_last_updated: Optional[datetime.datetime]
    organizations: Optional[List[Organization]] = None

    class Config:
        orm_mode = True
        segments = {"organizations": ["organizations"]}


class CurrentRole(BaseModel):
    title: str
    district: Union[str, int]
    division_id: str
    org_classification: OrgClassification

    class Config:
        orm_mode = True


class AltIdentifier(BaseModel):
    scheme: str
    identifier: str


class AltName(BaseModel):
    scheme: str
    name: str


class Link(BaseModel):
    link: str
    note: str


class Office(BaseModel):
    name: str
    fax: str
    voice: str
    email: str
    address: str


class Person(SegmentableBase):
    id: str
    name: str
    # jurisdiction: str
    jurisdiction_id: str = Field()
    party: str = Field()
    current_role: CurrentRole

    # extra_bio
    family_name: Optional[str]
    given_name: Optional[str]
    image: Optional[str]
    gender: Optional[str]
    birth_date: Optional[str]
    death_date: Optional[str]
    extras: Optional[dict]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    # join segments
    other_identifiers: Optional[List[AltIdentifier]]
    other_names: Optional[List[AltName]]
    links: Optional[List[Link]]
    sources: Optional[List[Link]]
    offices: Optional[List[Office]]

    class Config:
        orm_mode = True
