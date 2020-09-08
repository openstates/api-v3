import datetime
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field


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
    id: str = Field(
        ..., example="ocd-organization/32aab083-d7a0-44e0-9b95-a7790c542605"
    )
    name: str = Field(..., example="North Carolina General Assembly")
    classification: str = Field(..., example="legislature")

    class Config:
        orm_mode = True


class Jurisdiction(BaseModel):
    id: str = Field(..., example="ocd-jurisdiction/country:us/state:nc/government")
    name: str = Field(..., example="North Carolina")
    classification: JurisdictionClassification = Field(..., example="state")
    division_id: Optional[str] = Field(
        "", example="ocd-division/country:us/state:nc"
    )  # never exclude
    url: str = Field(..., example="https://nc.gov")
    # TODO: add these
    # people_last_updated: Optional[datetime.datetime]
    # bills_last_updated: Optional[datetime.datetime]
    organizations: Optional[List[Organization]] = None

    class Config:
        orm_mode = True


class CurrentRole(BaseModel):
    title: str = Field(..., example="Senator")
    org_classification: OrgClassification = Field(..., example="upper")
    district: Union[str, int, None] = Field("", example=3)
    division_id: Optional[str] = Field(
        "", example="ocd-division/country:us/state:nc/sldu:3"
    )

    class Config:
        orm_mode = True


class AltIdentifier(BaseModel):
    identifier: str = Field(..., example="NCL000123")
    scheme: str = Field(..., example="legacy_openstates")

    class Config:
        orm_mode = True


class AltName(BaseModel):
    name: str = Field(..., example="Auggie")
    note: str = Field(..., example="nickname")

    class Config:
        orm_mode = True


class Link(BaseModel):
    url: str = Field(..., example="https://example.com/")
    note: str = Field(..., example="homepage")

    class Config:
        orm_mode = True


class Office(BaseModel):
    name: str = Field(..., example="District Office")
    fax: Optional[str] = Field(None, example="919-555-1234")
    voice: Optional[str] = Field(None, example="919-555-0064")
    email: Optional[str] = Field(None, example="aperson@example.com")
    address: Optional[str] = Field(None, example="212 Maple Lane; Raleigh NC; 27526")

    class Config:
        orm_mode = True


class CompactJurisdiction(BaseModel):
    id: str = Field(..., example="ocd-jurisdiction/country:us/state:nc/government")
    name: str = Field(..., example="North Carolina")
    classification: JurisdictionClassification = Field(..., example="state")

    class Config:
        orm_mode = True


class Person(BaseModel):
    id: str = Field(..., example="ocd-person/adb58f21-f2fd-4830-85b6-f490b0867d14")
    name: str = Field(..., example="Angela Augusta")
    jurisdiction: CompactJurisdiction
    party: str = Field(..., example="Democratic")
    current_role: Optional[CurrentRole]

    # extra detail
    given_name: str = Field(..., example="Angela")
    family_name: str = Field(..., example="Augusta")
    image: str = Field(..., example="https://example.com/ncimg/3.png")
    gender: str = Field(..., example="female")
    birth_date: str = Field(..., example="1960-05-04")
    death_date: str = Field(..., example="2019-04-10")
    extras: dict = Field(..., example={"profession": "Doctor"})
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
    # TODO: use this on Bill and Jurisdiction
    identifier: str
    name: str
    classification: str
    start_date: str
    end_date: str

    class Config:
        orm_mode = True


class BillAbstract(BaseModel):
    abstract: str = Field(..., example="This bill designates a new state arachnid.")
    note: str = Field(..., example="house abstract")
    # TODO: remove these?
    # date: str = Field(..., example="2020-07-04")

    class Config:
        orm_mode = True


class BillTitle(BaseModel):
    title: str = Field(..., example="Designating the scorpion as the state arachnid.")
    note: str = Field(..., example="short title")

    class Config:
        orm_mode = True


class BillIdentifier(BaseModel):
    identifier: str = Field(..., example="HB 74")
    # TODO: remove these?
    # scheme: str = Field(..., "")
    # note: str = Field(..., "")

    class Config:
        orm_mode = True


class BillSponsorship(BaseModel):
    name: str = Field(..., example="JONES")
    entity_type: str = Field(..., example="person")
    organization: Optional[Organization] = Field(None, example=None)
    person: Optional[Person]
    primary: bool
    classification: str = Field(..., example="primary")

    class Config:
        orm_mode = True


class BillAction(BaseModel):
    organization: Organization
    description: str = Field(..., example="Passed 1st Reading")
    date: str = Field(..., example="2020-03-14")
    # TODO: enumerate billaction classifiers
    classification: List[str] = Field(..., example=["passed"])
    order: int
    extras: dict

    class Config:
        orm_mode = True


class BillDocumentLink(BaseModel):
    url: str = Field(..., example="https://example.com/doc.pdf")
    media_type: str = Field(..., example="application/pdf")

    class Config:
        orm_mode = True


class BillDocumentOrVersion(BaseModel):
    note: str = Field(..., example="Latest Version")
    date: str = Field(..., example="2020-10-01")
    links: List[BillDocumentLink]

    class Config:
        orm_mode = True


class VoteCount(BaseModel):
    option: str = Field(..., example="yes")
    value: int = Field(..., example=48)

    class Config:
        orm_mode = True


class PersonVote(BaseModel):
    option: str = Field(..., example="no")
    voter_name: str = Field(..., example="Wu")
    voter: Optional[Person]

    class Config:
        orm_mode = True


class VoteEvent(BaseModel):
    id: str
    motion_text: str = Field(..., example="Shall the bill be passed?")
    motion_classification: List[str] = Field([], example=["passage"])
    start_date: str = Field(..., example="2020-09-18")
    result: str = Field(..., example="pass")
    identifier: str = Field(..., example="HV #3312")
    extras: dict = dict

    organization: Organization
    votes: List[PersonVote]
    counts: List[VoteCount]
    sources: List[Link]

    class Config:
        orm_mode = True


class Bill(BaseModel):
    id: str = Field(..., example="ocd-bill/f0049138-1ad8-4506-a2a4-f4dd1251bbba")
    session: str = Field(..., example="2020")
    jurisdiction: CompactJurisdiction
    identifier: str = Field(..., example="SB 113")
    title: str = Field(..., example="Adopting a State Scorpion")
    classification: List[str] = Field([], example=["resolution"])
    subject: List[str] = Field([], example=["SCORPIONS", "SYMBOLS"])
    extras: dict = Field({}, example={})
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
