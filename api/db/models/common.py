import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class PrimaryUUID:
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)


class LinkBase(PrimaryUUID):
    url = Column(String)
    note = Column(String)


class RelatedEntityBase(PrimaryUUID):
    name = Column(String)
    entity_type = Column(String)

    @declared_attr
    def organization_id(cls):
        return Column("organization_id", ForeignKey("opencivicdata_organization.id"))

    @declared_attr
    def organization(cls):
        return relationship("Organization")

    @declared_attr
    def person_id(cls):
        return Column("person_id", ForeignKey("opencivicdata_person.id"))

    @declared_attr
    def person(cls):
        return relationship("Organization")
