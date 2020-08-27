from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from .. import Base
from .common import PrimaryUUID
from .jurisdiction import LegislativeSession
from .people_orgs import Organization, Person
from .bills import Bill


class VoteEvent(Base):
    __tablename__ = "opencivicdata_voteevent"

    id = Column(String, primary_key=True, index=True)
    identifier = Column(String)
    motion_text = Column(String)
    motion_classification = Column(ARRAY(String))
    start_date = Column(String)
    result = Column(String)
    extras = Column(JSONB)

    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    legislative_session_id = Column(UUID, ForeignKey(LegislativeSession.id))
    legislative_session = relationship(LegislativeSession)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)


class VoteCount(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_votecount"

    vote_event_id = Column(String, ForeignKey(Bill.id))
    vote_event = relationship(Bill)

    option = Column(String)
    value = Column(Integer)


class VoteSource(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_votesource"

    vote_event_id = Column(String, ForeignKey(Bill.id))
    vote_event = relationship(Bill)

    url = Column(String)
    note = Column(String)


class PersonVote(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_personvote"

    vote_event_id = Column(String, ForeignKey(Bill.id))
    vote_event = relationship(Bill)

    option = Column(String)
    voter_name = Column(String)
    voter_id = Column(String, ForeignKey(Person.id))
    voter = relationship(Person)
    note = Column(String)
