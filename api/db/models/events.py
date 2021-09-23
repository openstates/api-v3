from .. import Base
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    #     Integer,
    Boolean,
    Text,
    # ARRAY,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .common import PrimaryUUID  # , RelatedEntityBase
from .jurisdiction import Jurisdiction

# from .bills import Bill
# from .votes import VoteEvent


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
    location_id = Column(String, ForeignKey(EventLocation.id))
    location = relationship(EventLocation)

    # participants = relationship("EventParticipant")
    # documents = relationship("EventDocument")
    # media = relationship("EventMedia")
    # agenda = relationship("EventAgendaItem")


# class EventMediaBase(Base):
#     __tablename__ = "opencivicdata_eventmediabase"

#     note = Column(String)
#     date = Column(String)
#     offset = Column(Integer)


# class EventMedia(EventMediaBase):
#     __tablename__ = "opencivicdata_eventmedia"

#     event = relationship("Event")
#     classification = Column(String)
#     links = Column(JSONB)


# class EventDocument(Base):
#     __tablename__ = "opencivicdata_eventdocument"

#     event = relationship("Event")
#     note = Column(String)
#     date = Column(String)
#     classification = Column(String)
#     links = Column(JSONB)


# class EventParticipant(RelatedEntityBase):
#     __tablename__ = "opencivicdata_eventparticipant"

#     event = relationship("Event")
#     note = Column(Text)


# class EventAgendaItem(Base):
#     __tablename__ = "opencivicdata_eventagendaitem"

#     description = Column(Text)
#     classification = Column(ARRAY)
#     order = Column(Integer)
#     subjects = Column(ARRAY)
#     notes = Column(ARRAY)
#     event = relationship("Event")
#     extras = Column(JSONB)

#     media = relationship("EventAgendaMedia")  # , back_populates="eventagendamedialink")


# class EventRelatedEntity(RelatedEntityBase):
#     __tablename__ = "opencivicdata_eventrelatedentity"

#     agenda_item_id = Column(String, ForeignKey(EventAgendaItem.id))
#     agenda_item = relationship("EventAgendaItem")

#     bill_id = Column(String, ForeignKey(Bill.id))
#     bill = relationship("Bill")
#     vote_event_id = Column(String, ForeignKey(VoteEvent.id))
#     vote_event = relationship("VoteEvent")
#     note = Column(Text)


# class EventAgendaMedia(EventMediaBase):
#     __tablename__ = "opencivicdata_eventagendamedia"

#     agenda_item_id = Column(String, ForeignKey(EventAgendaItem.id))
#     agenda_item = relationship("EventAgendaItem")

#     classification = Column(String)
#     links = Column(JSONB)
