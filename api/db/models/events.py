from .. import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime, Text, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType # is this a thing?
from .common import LinkBase, RelatedEntityBase # what is is MimetypeLinkBase?
from .jurisdiction import Jurisdiction
from .bills import Bill
from .votes import VoteEvent


class Event(Base):
    __tablename__ = "opencivicdata_event"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    jurisdiction = Column(String)
    description = Column(Text)
    classification = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    all_day = Column(Boolean)
    status = Column(String)

    eventparticipant = relationship("EventParticipant")
    eventsource = relationship("EventSource")
    eventlink = relationship("EventLink")
    eventdocument = relationship("EventDocument", back_populates="eventdocumentlink")
    eventmedia = relationship("EventMedia", back_populates="eventmedialink")
    eventagendaitem = relationship("EventAgendaItem", back_populates="eventrelatedentity")


class EventMediaBase(Base):
    __tablename__ = "opencivicdata_eventmediabase"

    note = Column(String)
    date = Column(DateTime)
    offset = Column(Integer)


class EventLocation(Base):
    __tablename__ = "opencivicdata_eventlocation"

    name = Column(String)
    url = Column(URLType) # is this the correct type?
    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")


class EventMedia(EventMediaBase):
    __tablename__ = "opencivicdata_eventmedia"

    event = relationship("Event")
    classification = Column(String)
    eventmedialink = relationship("EventMediaLink")


class EventMediaLink(MimetypeLinkBase):
    __tablename__ = "opencivicdata_eventmedialink"

    media = relationship("EventMedia")


class EventDocument(Base):
    __tablename__ = "opencivicdata_eventdocument"

    event = relationship("Event")
    note = Column(String)
    date = Column(DateTime)
    classification = Column(String)
    eventdocumentlink = relationship("EventDocumentLink")


class EventDocumentLink(MimetypeLinkBase):
    __tablename__ = "opencivicdata_eventdocumentlink"

    document = relationship("EventDocument")


class EventLink(LinkBase):
    __tablename__ = "opencivicdata_eventlink"

    event = relationship("Event")


class EventSource(LinkBase):
    __tablename__ = "opencivicdata_eventsource"

    event = relationship("Event")


class EventParticipant(RelatedEntityBase):
    __tablename__ = "opencivicdata_eventparticipant"

    event = relationship("Event")
    note = Column(Text)


class EventAgendaItem(Base):
    __tablename__ = "opencivicdata_eventagendaitem"

    description = Column(Text)
    classification = Column(ARRAY)
    order = Column(Integer)
    subjects = Column(ARRAY)
    notes = Column(ARRAY)
    event = relationship("Event")
    extras = Column(JSON)
    eventagendamedia = relationship("EventAgendaMedia", back_populates="eventagendamedialink")
    eventrelatedentity = relationship("EventRelatedEntity")


class EventRelatedEntity(RelatedEntityBase):
    __tablename__ = "opencivicdata_eventrelatedentity"

    agenda_item = relationship("EventAgendaItem")
    # will just unresolve if needed
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship("Bill")
    vote_event_id = Column(String, ForeignKey(VoteEvent.id))
    vote_event = relationship("VoteEvent")
    note = Column(Text)


class EventAgendaMedia(EventMediaBase):
    __tablename__ = "opencivicdata_eventagendamedia"

    classification = Column(String)
    eventagendaitem = relationship("EventAgendaItem")
    eventagendamedialink = relationship("EventAgendaMediaLink")


class EventAgendaMediaLink(MimetypeLinkBase):
    __tablename__ = "opencivicdata_eventagendamedialink"

    media = relationship("EventAgendaMedia")
