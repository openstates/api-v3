import datetime
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel


class IncludeBase(BaseModel):
    @classmethod
    def with_includes(Cls, obj, includes):
        newobj = Cls.from_orm(obj)
        for include in Cls.__config__.includes:
            if include not in includes:
                setattr(newobj, include, None)
        return newobj


class JurisdictionClassification(str, Enum):
    state = "state"
    municipality = "municipality"
    government = "government"  # TODO: remove this before release


class OrgClassification(str, Enum):
    legislature = "legislature"
    executive = "executive"
    lower = "lower"
    upper = "upper"
    government = "government"


# class LegislativeSessionClassification(str, Enum):
#     primary = "primary"
#     special = "special"
#     unset = ""


class Organization(BaseModel):
    id: str
    name: str
    classification: str

    class Config:
        orm_mode = True


class Jurisdiction(IncludeBase):
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
        includes = ["organizations"]


class CurrentRole(BaseModel):
    title: str
    org_classification: OrgClassification
    district: Union[str, int, None] = ""
    division_id: Optional[str] = ""

    class Config:
        orm_mode = True


class AltIdentifier(BaseModel):
    identifier: str
    scheme: str

    class Config:
        orm_mode = True


class AltName(BaseModel):
    name: str
    note: str

    class Config:
        orm_mode = True


class Link(BaseModel):
    url: str
    note: str

    class Config:
        orm_mode = True


class Office(BaseModel):
    name: str
    fax: Optional[str]
    voice: Optional[str]
    email: Optional[str]
    address: Optional[str]

    class Config:
        orm_mode = True


class CompactJurisdiction(BaseModel):
    id: str
    name: str
    classification: JurisdictionClassification

    class Config:
        orm_mode = True


class Person(IncludeBase):
    id: str
    name: str
    jurisdiction: CompactJurisdiction
    party: str
    current_role: Optional[CurrentRole]

    # TODO: make these required?
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

    # joins
    other_identifiers: Optional[List[AltIdentifier]]
    other_names: Optional[List[AltName]]
    links: Optional[List[Link]]
    sources: Optional[List[Link]]
    offices: Optional[List[Office]]

    class Config:
        orm_mode = True
        includes = ["other_names", "other_identifiers", "links", "sources", "offices"]


class LegislativeSession(BaseModel):
    identifier: str
    name: str
    classification: str
    start_date: str
    end_date: str

    class Config:
        orm_mode = True


class BillAbstract(BaseModel):
    abstract: str
    note: str
    date: str

    class Config:
        orm_mode = True


class BillTitle(BaseModel):
    title: str
    note: str

    class Config:
        orm_mode = True


class BillIdentifier(BaseModel):
    identifier: str
    scheme: str
    note: str

    class Config:
        orm_mode = True


class BillSponsorship(BaseModel):
    name: str
    entity_type: str  # TODO: enum organization or person?
    organization: Optional[Organization]
    person: Optional[Person]
    primary: bool
    classification: str

    class Config:
        orm_mode = True


class BillAction(BaseModel):
    organization: Organization
    description: str
    date: str
    classification: List[str]
    order: int
    extras: dict

    class Config:
        orm_mode = True


class Bill(IncludeBase):
    id: str
    session: str
    jurisdiction: CompactJurisdiction
    identifier: str
    title: str
    classification: List[str] = list
    subject: List[str] = list
    extras: dict = dict
    created_at: datetime.datetime
    updated_at: datetime.datetime

    abstracts: Optional[List[BillAbstract]]
    other_titles: Optional[List[BillTitle]]
    other_identifiers: Optional[List[BillIdentifier]]
    sponsorships: Optional[List[BillSponsorship]]
    actions: Optional[List[BillAction]]
    sources: Optional[List[Link]]

    class Config:
        orm_mode = True
        includes = [
            "abstracts",
            "other_titles",
            "other_identifiers",
            "actions",
            "sponsorships",
            "sources",
        ]
