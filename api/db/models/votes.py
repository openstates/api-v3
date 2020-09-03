from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from .. import Base
from .common import PrimaryUUID, LinkBase
from .jurisdiction import LegislativeSession
from .people_orgs import Organization, Person
from .bills import Bill, BillAction


class VoteEvent(Base):
    __tablename__ = "opencivicdata_voteevent"

    id = Column(String, primary_key=True, index=True)
    identifier = Column(String)
    motion_text = Column(String)
    motion_classification = Column(ARRAY(Text), default=list)
    start_date = Column(String)
    result = Column(String)
    extras = Column(JSONB, default=dict)

    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    legislative_session_id = Column(UUID, ForeignKey(LegislativeSession.id))
    legislative_session = relationship(LegislativeSession)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    bill_action_id = Column(UUID, ForeignKey(BillAction.id))
    bill_action = relationship(BillAction)

    votes = relationship("PersonVote")
    counts = relationship("VoteCount")
    sources = relationship("VoteSource")


class VoteCount(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_votecount"

    vote_event_id = Column(String, ForeignKey(VoteEvent.id))
    vote_event = relationship(VoteEvent)

    option = Column(String)
    value = Column(Integer)


class VoteSource(LinkBase, Base):
    __tablename__ = "opencivicdata_votesource"

    vote_event_id = Column(String, ForeignKey(VoteEvent.id))
    vote_event = relationship(VoteEvent)


class PersonVote(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_personvote"

    vote_event_id = Column(String, ForeignKey(VoteEvent.id))
    vote_event = relationship(VoteEvent)

    option = Column(String)
    voter_name = Column(String)
    voter_id = Column(String, ForeignKey(Person.id))
    voter = relationship(Person)
    note = Column(String)  # TODO: check this field
