from .. import Base
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Boolean,
    Text,
    ARRAY,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .common import PrimaryUUID, RelatedEntityBase
from .jurisdiction import Jurisdiction
from .bills import Bill
from .votes import VoteEvent


class EventLocation(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_eventlocation"

    name = Column(String)
    url = Column(String)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")


class Event(Base):
    __tablename__ = "opencivicdata_event"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    classification = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    all_day = Column(Boolean)
    status = Column(String)
    upstream_id = Column(String)
    deleted = Column(Boolean)

    sources = Column(JSONB)
    links = Column(JSONB)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship(Jurisdiction)
    location_id = Column(UUID, ForeignKey(EventLocation.id))
    location = relationship(EventLocation)

    media = relationship("EventMedia", back_populates="event")
    documents = relationship("EventDocument", back_populates="event")
    participants = relationship("EventParticipant", back_populates="event")
    agenda = relationship("EventAgendaItem", back_populates="event")


class EventMediaBase(PrimaryUUID):
    note = Column(String)
    date = Column(String)
    offset = Column(Integer)
    classification = Column(String)
    links = Column(JSONB)


class EventMedia(EventMediaBase, Base):
    __tablename__ = "opencivicdata_eventmedia"

    event_id = Column(String, ForeignKey(Event.id))
    event = relationship(Event, back_populates="media")


class EventDocument(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_eventdocument"

    event_id = Column(String, ForeignKey(Event.id))
    event = relationship("Event", back_populates="documents")

    note = Column(String)
    date = Column(String)
    classification = Column(String)
    links = Column(JSONB)


class EventParticipant(RelatedEntityBase, Base):
    __tablename__ = "opencivicdata_eventparticipant"

    event_id = Column(String, ForeignKey(Event.id))
    event = relationship("Event", back_populates="participants")

    note = Column(Text)


class EventAgendaItem(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_eventagendaitem"

    event_id = Column(String, ForeignKey(Event.id))
    event = relationship("Event", back_populates="agenda")

    description = Column(Text)
    classification = Column(ARRAY(Text))
    order = Column(Integer)
    subjects = Column(ARRAY(Text))
    notes = Column(ARRAY(Text))
    extras = Column(JSONB)

    related_entities = relationship("EventRelatedEntity", back_populates="agenda_item")
    media = relationship("EventAgendaMedia", back_populates="agenda_item")


class EventRelatedEntity(RelatedEntityBase, Base):
    __tablename__ = "opencivicdata_eventrelatedentity"

    agenda_item_id = Column(UUID, ForeignKey(EventAgendaItem.id))
    agenda_item = relationship(EventAgendaItem)

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    vote_event_id = Column(String, ForeignKey(VoteEvent.id))
    vote_event = relationship(VoteEvent)
    note = Column(Text)


class EventAgendaMedia(EventMediaBase, Base):
    __tablename__ = "opencivicdata_eventagendamedia"

    agenda_item_id = Column(UUID, ForeignKey(EventAgendaItem.id))
    agenda_item = relationship(EventAgendaItem)
