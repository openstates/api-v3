from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from .. import Base
from .jurisdiction import LegislativeSession
from .people_orgs import Organization, Person


class Bill(Base):
    __tablename__ = "opencivicdata_bill"

    id = Column(String, primary_key=True, index=True)
    identifier = Column(String)
    title = Column(String)
    classification = Column(ARRAY(String))
    subject = Column(ARRAY(String))
    extras = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    from_organization_id = Column(String, ForeignKey(Organization.id))
    from_organization = relationship("Organization")
    legislative_session_id = Column(UUID, ForeignKey(LegislativeSession.id))
    legislative_session = relationship("LegislativeSession")

    abstracts = relationship("BillAbstract")
    other_titles = relationship("BillTitle")
    other_identifiers = relationship("BillIdentifier")
    sponsorships = relationship("BillSponsorship")
    actions = relationship("BillAction")
    sources = relationship("BillSource")

    @property
    def jurisdiction(self):
        return self.legislative_session.jurisdiction

    @property
    def session(self):
        return self.legislative_session.identifier

    # computed fields
    first_action_date = Column(String)
    latest_action_date = Column(String)
    latest_action_description = Column(String)
    latest_passage_date = Column(String)


class BillAbstract(Base):
    __tablename__ = "opencivicdata_billabstract"

    id = Column(UUID, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    abstract = Column(String)
    note = Column(String)
    date = Column(String)


class BillTitle(Base):
    __tablename__ = "opencivicdata_billtitle"

    id = Column(UUID, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    title = Column(String)
    note = Column(String)


class BillIdentifier(Base):
    __tablename__ = "opencivicdata_billidentifier"

    id = Column(UUID, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    identifier = Column(String)
    scheme = Column(String)
    note = Column(String)


class BillSource(Base):
    __tablename__ = "opencivicdata_billsource"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    url = Column(String)
    note = Column(String)


class BillSponsorship(Base):
    __tablename__ = "opencivicdata_billsponsorship"

    id = Column(UUID, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    name = Column(String)
    entity_type = Column(String)
    primary = Column(Boolean)
    classification = Column(String)
    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)


class BillAction(Base):
    __tablename__ = "opencivicdata_billaction"

    id = Column(UUID, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    description = Column(String)
    date = Column(String)
    classification = Column(ARRAY(String))
    order = Column(Integer)
    extras = Column(JSONB)


# class BillActionRelatedEntity(Base):
#     __tablename__ "opencivicdata_billactionrelatedentity"

#     id = Column(UUID, primary_key=True, index=True)
#     action_id = Column(String, ForeignKey(BillAction.id))
#     action = relationship(BillAction)


class SearchableBill(Base):
    __tablename__ = "opencivicdata_searchablebill"

    id = Column(Integer, primary_key=True, index=True)
    search_vector = Column(TSVECTOR)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
