import datetime
from typing import Optional, List, Union
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class JurisdictionClassification(str, Enum):
    state = "state"
    municipality = "municipality"
    country = "country"


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


class Post(BaseModel):
    label: str = Field(..., example="2")
    role: str = Field(..., example="Senator")
    division_id: str = Field(..., example="ocd-division/country:us/state:mn/sldu:4")
    maximum_memberships: int = Field(..., example=1)

    class Config:
        orm_mode = True


class Organization(BaseModel):
    id: str = Field(
        ..., example="ocd-organization/32aab083-d7a0-44e0-9b95-a7790c542605"
    )
    name: str = Field(..., example="North Carolina General Assembly")
    classification: str = Field(..., example="legislature")

    class Config:
        orm_mode = True


class Chamber(Organization):
    districts: Optional[List[Post]] = None


class DataExport(BaseModel):
    created_at: datetime.datetime
    updated_at: datetime.datetime
    data_type: str
    url: str

    class Config:
        orm_mode = True


class LegislativeSession(BaseModel):
    identifier: str
    name: str
    classification: str
    start_date: str
    end_date: str
    downloads: Optional[List[DataExport]]

    class Config:
        orm_mode = True


class RunPlan(BaseModel):
    success: bool
    start_time: datetime.datetime
    end_time: datetime.datetime

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
    latest_bill_update: datetime.datetime
    latest_people_update: datetime.datetime
    organizations: Optional[List[Chamber]] = None
    legislative_sessions: Optional[List[LegislativeSession]] = None
    latest_runs: Optional[List[RunPlan]] = None

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
    note: Union[str, None] = Field(None, example="homepage")

    class Config:
        orm_mode = True


class Office(BaseModel):
    name: str = Field(..., example="District Office")
    fax: Optional[str] = Field(None, example="919-555-1234")
    voice: Optional[str] = Field(None, example="919-555-0064")
    address: Optional[str] = Field(None, example="212 Maple Lane; Raleigh NC; 27526")
    classification: Optional[str] = Field(None, example="capitol")

    class Config:
        orm_mode = True


class CompactJurisdiction(BaseModel):
    id: str = Field(..., example="ocd-jurisdiction/country:us/state:nc/government")
    name: str = Field(..., example="North Carolina")
    classification: JurisdictionClassification = Field(..., example="state")

    class Config:
        orm_mode = True


class CompactPerson(BaseModel):
    id: str = Field(..., example="ocd-person/adb58f21-f2fd-4830-85b6-f490b0867d14")
    name: str = Field(..., example="Angela Augusta")
    party: str = Field(..., example="Democratic")
    current_role: Optional[CurrentRole]

    class Config:
        orm_mode = True


class CompactBill(BaseModel):
    id: str = Field(..., example="ocd-bill/12345678-0000-1111-2222-333344445555")
    session: str
    identifier: str
    title: str

    class Config:
        orm_mode = True


class CompactVoteEvent(BaseModel):
    id: str = Field(..., example="ocd-vote/12345678-0000-1111-2222-333344445555")
    motion_text: str = Field(..., example="Shall the bill be passed?")

    class Config:
        orm_mode = True


class Person(CompactPerson):
    jurisdiction: CompactJurisdiction

    # extra detail
    given_name: str = Field(..., example="Angela")
    family_name: str = Field(..., example="Augusta")
    image: str = Field(..., example="https://example.com/ncimg/3.png")
    email: str = Field(..., example="aperson@example.com")
    gender: str = Field(..., example="female")
    birth_date: str = Field(..., example="1960-05-04")
    death_date: str = Field(..., example="2019-04-10")
    extras: dict = Field(..., example={"profession": "Doctor"})
    created_at: datetime.datetime
    updated_at: datetime.datetime
    openstates_url: str = Field(
        ...,
        example="https://openstates.org/person/amos-l-quick-iii-28NRPPfJA6FGVl9RrjpKjl/",
    )

    # joins
    other_identifiers: Optional[List[AltIdentifier]]
    other_names: Optional[List[AltName]]
    links: Optional[List[Link]]
    sources: Optional[List[Link]]
    offices: Optional[List[Office]]

    class Config:
        orm_mode = True


class RelatedBill(BaseModel):
    identifier: str = Field(..., example="HB 123")
    legislative_session: str = Field(..., example="2022S1")
    relation_type: str = Field(..., example="companion")

    class Config:
        orm_mode = True


class BillAbstract(BaseModel):
    abstract: str = Field(..., example="This bill designates a new state arachnid.")
    note: str = Field(..., example="house abstract")

    class Config:
        orm_mode = True


class BillTitle(BaseModel):
    title: str = Field(..., example="Designating the scorpion as the state arachnid.")
    note: str = Field(..., example="short title")

    class Config:
        orm_mode = True


class BillIdentifier(BaseModel):
    identifier: str = Field(..., example="HB 74")

    class Config:
        orm_mode = True


class BillSponsorship(BaseModel):
    id: UUID = Field(..., example="f0049138-1ad8-4506-a2a4-f4dd1251bbba")
    name: str = Field(..., example="JONES")
    entity_type: str = Field(..., example="person")
    organization: Optional[Organization] = Field(None, example=None)
    person: Optional[CompactPerson]
    primary: bool
    classification: str = Field(..., example="primary")
    
    class Config:
        orm_mode = True

class BillActionRelatedEntity(BaseModel):
    name: str = Field(..., example="Senate Committee of the Whole")
    entity_type: str = Field(..., example="organization")
    organization: Optional[Organization] = Field(None, example=None)
    person: Optional[CompactPerson]

    class Config:
        orm_mode = True


class BillAction(BaseModel):
    id: UUID = Field(..., example="f0049138-1ad8-4506-a2a4-f4dd1251bbba")
    organization: Organization
    description: str = Field(..., example="Passed 1st Reading")
    date: str = Field(..., example="2020-03-14")
    # TODO: enumerate billaction classifiers
    classification: List[str] = Field(..., example=["passed"])
    order: int
    related_entities: Optional[List[BillActionRelatedEntity]]

    class Config:
        orm_mode = True


class BillDocumentLink(BaseModel):
    url: str = Field(..., example="https://example.com/doc.pdf")
    media_type: str = Field(..., example="application/pdf")

    class Config:
        orm_mode = True


class BillDocumentOrVersion(BaseModel):
    id: UUID = Field(..., example="f0049138-1ad8-4506-a2a4-f4dd1251bbba")
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
    id: UUID = Field(..., example="f0049138-1ad8-4506-a2a4-f4dd1251bbba")
    option: str = Field(..., example="no")
    voter_name: str = Field(..., example="Wu")
    voter: Optional[CompactPerson]

    class Config:
        orm_mode = True

class VoteEvent(BaseModel):
    id: str
    motion_text: str = Field(..., example="Shall the bill be passed?")
    motion_classification: List[str] = Field([], example=["passage"])
    start_date: str = Field(..., example="2020-09-18")
    result: str = Field(..., example="pass")
    identifier: str = Field(..., example="HV #3312")
    extras: dict

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
    from_organization: Organization
    identifier: str = Field(..., example="SB 113")
    title: str = Field(..., example="Adopting a State Scorpion")
    classification: List[str] = Field([], example=["resolution"])
    subject: List[str] = Field([], example=["SCORPIONS", "SYMBOLS"])
    extras: dict = Field({}, example={})
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # computed fields
    openstates_url: str = Field(
        ..., example="https://openstates.org/nc/bills/2019/HB1105/"
    )
    first_action_date: Optional[str] = Field("", example="2020-01-01")
    latest_action_date: Optional[str] = Field("", example="2020-02-01")
    latest_action_description: Optional[str] = Field("", example="Introduced in House")
    latest_passage_date: Optional[str] = Field("", example="2020-03-01")

    related_bills: Optional[List[RelatedBill]]
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


class CommitteeClassification(str, Enum):
    committee = "committee"
    subcommittee = "subcommittee"


class CommitteeMembership(BaseModel):
    person_name: str
    role: str
    person: Optional[CompactPerson]

    class Config:
        orm_mode = True


class Committee(BaseModel):
    id: str = Field(
        ..., example="ocd-organization/aabbbbcc-dddd-eeee-ffff-0123456789ab"
    )
    name: str = Field(..., example="Health & Public Services")
    classification: CommitteeClassification
    parent_id: str = Field(
        ..., example="ocd-organization/aabbbbcc-dddd-eeee-ffff-999988887777"
    )
    extras: dict = Field(..., example={"room": "Room 4B"})

    # joins
    memberships: Optional[List[CommitteeMembership]]
    other_names: Optional[List[AltName]]
    links: Optional[List[Link]]
    sources: Optional[List[Link]]

    class Config:
        orm_mode = True


class EventLocation(BaseModel):
    name: str
    url: str

    class Config:
        orm_mode = True


class EventMedia(BaseModel):
    note: str
    date: str
    offset: Union[int, None]
    classification: str
    links: list[Link]

    class Config:
        orm_mode = True


class EventDocument(BaseModel):
    note: str
    date: str
    classification: str
    links: list[Link]

    class Config:
        orm_mode = True


class EventParticipant(BaseModel):
    note: str
    name: str = Field(..., example="JONES")
    entity_type: str = Field(..., example="person")
    organization: Optional[Organization] = Field(None, example=None)
    person: Optional[CompactPerson]

    class Config:
        orm_mode = True


class EventRelatedEntity(BaseModel):
    note: str
    name: str = Field(..., example="JONES")
    entity_type: str = Field(..., example="person")
    organization: Optional[Organization] = Field(None, example=None)
    person: Optional[CompactPerson]
    bill: Optional[CompactBill]
    vote: Optional[CompactVoteEvent]

    class Config:
        orm_mode = True


class EventAgendaItem(BaseModel):
    description: str
    classification: List[str]
    order: int
    subjects: List[str]
    notes: List[str]
    extras: dict

    related_entities: List[EventRelatedEntity]
    media: List[EventMedia]

    class Config:
        orm_mode = True


class Event(BaseModel):
    id: str
    name: str
    jurisdiction: CompactJurisdiction
    description: str
    classification: str
    start_date: str
    end_date: str
    all_day: bool
    status: str
    upstream_id: str
    deleted: bool
    location: Optional[EventLocation]

    # related fields
    links: Optional[List[Link]]
    sources: Optional[List[Link]]
    media: Optional[List[EventMedia]]
    documents: Optional[List[EventDocument]]
    participants: Optional[List[EventParticipant]]
    agenda: Optional[List[EventAgendaItem]]

    class Config:
        orm_mode = True
