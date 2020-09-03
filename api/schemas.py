import datetime
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel


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


class Jurisdiction(BaseModel):
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


class Person(BaseModel):
    id: str
    name: str
    jurisdiction: CompactJurisdiction
    party: str
    current_role: Optional[CurrentRole]

    # extra detail
    family_name: str
    given_name: str
    image: str
    gender: str
    birth_date: str
    death_date: str
    extras: dict
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # joins
    other_identifiers: Optional[List[AltIdentifier]]
    other_names: Optional[List[AltName]]
    links: Optional[List[Link]]
    sources: Optional[List[Link]]
    offices: Optional[List[Office]]

    class Config:
        orm_mode = True


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


class BillDocumentLink(BaseModel):
    url: str
    media_type: str

    class Config:
        orm_mode = True


class BillDocumentOrVersion(BaseModel):
    note: str
    date: str
    links: List[BillDocumentLink]

    class Config:
        orm_mode = True


class VoteCount(BaseModel):
    option: str
    value: int

    class Config:
        orm_mode = True


class PersonVote(BaseModel):
    option: str
    voter_name: str
    voter: Optional[Person]

    class Config:
        orm_mode = True


class VoteEvent(BaseModel):
    id: str
    identifier: str
    motion_text: str
    motion_classification: List[str] = list
    start_date: str
    result: str
    extras: dict = dict

    organization: Organization
    votes: List[PersonVote]
    counts: List[VoteCount]
    sources: List[Link]

    class Config:
        orm_mode = True


class Bill(BaseModel):
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
    versions: Optional[List[BillDocumentOrVersion]]
    documents: Optional[List[BillDocumentOrVersion]]
    votes: Optional[List[VoteEvent]]

    class Config:
        orm_mode = True
