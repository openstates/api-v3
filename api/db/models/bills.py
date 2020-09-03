from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
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
    # important for ARRAY types to use Text to avoid casting to String
    classification = Column(ARRAY(Text))
    subject = Column(ARRAY(Text))
    extras = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    from_organization_id = Column(String, ForeignKey(Organization.id))
    from_organization = relationship("Organization")
    legislative_session_id = Column(
        UUID(as_uuid=True), ForeignKey(LegislativeSession.id)
    )
    legislative_session = relationship("LegislativeSession")

    abstracts = relationship("BillAbstract")
    other_titles = relationship("BillTitle")
    other_identifiers = relationship("BillIdentifier")
    sponsorships = relationship("BillSponsorship")
    actions = relationship("BillAction")
    sources = relationship("BillSource")
    documents = relationship("BillDocument")
    versions = relationship("BillVersion")
    votes = relationship("VoteEvent")

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


class BillRelatedBase(PrimaryUUID):
    @declared_attr
    def bill_id(cls):
        return Column("bill_id", ForeignKey(Bill.id))

    @declared_attr
    def bill(cls):
        return relationship(Bill)


class BillAbstract(BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billabstract"

    abstract = Column(String)
    note = Column(String)
    date = Column(String)


class BillTitle(BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billtitle"

    title = Column(String)
    note = Column(String)


class BillIdentifier(BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billidentifier"

    identifier = Column(String)
    scheme = Column(String)
    note = Column(String)


class BillAction(BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billaction"

    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship(Organization)
    description = Column(String)
    date = Column(String)
    classification = Column(ARRAY(Text), default=list)
    order = Column(Integer)
    extras = Column(JSONB, default=dict)


class BillActionRelatedEntity(RelatedEntityBase, Base):
    __tablename__ = "opencivicdata_billactionrelatedentity"

    action_id = Column(UUID(as_uuid=True), ForeignKey(BillAction.id))
    action = relationship(BillAction)


class RelatedBill(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_relatedbill"

    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill, foreign_keys=[bill_id])
    related_bill_id = Column(String, ForeignKey(Bill.id))
    related_bill = relationship(Bill, foreign_keys=[related_bill_id])

    identifier = Column(String)
    legislative_session = Column(String)  # not a FK, it can be unknown
    relation_type = Column(String)


class BillSponsorship(RelatedEntityBase, BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billsponsorship"

    primary = Column(Boolean)
    classification = Column(String)


class BillSource(LinkBase, BillRelatedBase, Base):
    __tablename__ = "opencivicdata_billsource"


class DocVerBase(BillRelatedBase):
    """ base class for document & version """

    note = Column(String)
    date = Column(String)
    extras = Column(JSONB)


class DocumentLinkBase(PrimaryUUID):
    media_type = Column(String)
    url = Column(String)
    text = Column(String)


class BillDocument(DocVerBase, Base):
    __tablename__ = "opencivicdata_billdocument"

    links = relationship("BillDocumentLink")


class BillVersion(DocVerBase, Base):
    __tablename__ = "opencivicdata_billversion"

    links = relationship("BillVersionLink")


class BillDocumentLink(DocumentLinkBase, Base):
    __tablename__ = "opencivicdata_billdocumentlink"

    document_id = Column(UUID(as_uuid=True), ForeignKey(BillDocument.id))
    document = relationship(BillDocument)


class BillVersionLink(DocumentLinkBase, Base):
    __tablename__ = "opencivicdata_billversionlink"

    version_id = Column(UUID(as_uuid=True), ForeignKey(BillVersion.id))
    version = relationship(BillVersion)


class SearchableBill(Base):
    __tablename__ = "opencivicdata_searchablebill"

    id = Column(Integer, primary_key=True, index=True)
    search_vector = Column(TSVECTOR)
    bill_id = Column(String, ForeignKey(Bill.id))
    bill = relationship(Bill)
