from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from .. import Base
from .common import PrimaryUUID, LinkBase, RelatedEntityBase
from .jurisdiction import LegislativeSession
from .people_orgs import Organization


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


class BillAbstract(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_billabstract"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    abstract = Column(String)
    note = Column(String)
    date = Column(String)


class BillTitle(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_billtitle"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    title = Column(String)
    note = Column(String)


class BillIdentifier(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_billidentifier"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    identifier = Column(String)
    scheme = Column(String)
    note = Column(String)


class BillSource(LinkBase, Base):
    __tablename__ = "opencivicdata_billsource"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)


class BillSponsorship(RelatedEntityBase, Base):
    __tablename__ = "opencivicdata_billsponsorship"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    primary = Column(Boolean)
    classification = Column(String)


class BillAction(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_billaction"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    description = Column(String)
    date = Column(String)
    classification = Column(ARRAY(String))
    order = Column(Integer)
    extras = Column(JSONB)


# class BillActionRelatedEntity(RelatedEntityBase, Base):
#     __tablename__ "opencivicdata_billactionrelatedentity"

#     action_id = Column(String, ForeignKey(BillAction.id))
#     action = relationship(BillAction)


class SearchableBill(Base):
    __tablename__ = "opencivicdata_searchablebill"

    id = Column(Integer, primary_key=True, index=True)
    search_vector = Column(TSVECTOR)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
