import uuid
import base62
from slugify import slugify
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .. import Base
from .common import PrimaryUUID, LinkBase
from .jurisdiction import Jurisdiction


def encode_uuid(id):
    uuid_portion = str(id).split("/")[1]
    as_int = uuid.UUID(uuid_portion).int
    return base62.encode(as_int)


class Organization(Base):
    __tablename__ = "opencivicdata_organization"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    classification = Column(String)
    parent_id = Column(String, index=True)

    links = Column(JSONB)
    sources = Column(JSONB)
    extras = Column(JSONB, default=dict)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction", back_populates="organizations")

    posts = relationship("Post", order_by="Post.label", back_populates="organization")
    memberships = relationship("Membership", back_populates="organization")

    @property
    def districts(self):
        return self.posts


class Post(Base):
    __tablename__ = "opencivicdata_post"

    id = Column(String, primary_key=True, index=True)
    label = Column(String)
    role = Column(String)
    division_id = Column(String)
    maximum_memberships = Column(Integer)

    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship("Organization")


class Person(Base):
    __tablename__ = "opencivicdata_person"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    family_name = Column(String, default="")
    given_name = Column(String, default="")
    image = Column(String, default="")
    gender = Column(String, default="")
    email = Column(String, default="")
    biography = Column(String, default="")
    birth_date = Column(String, default="")
    death_date = Column(String, default="")
    party = Column("primary_party", String)
    current_role = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    extras = Column(JSONB, default=dict)
    jurisdiction_id = Column(
        "current_jurisdiction_id", String, ForeignKey(Jurisdiction.id)
    )
    jurisdiction = relationship("Jurisdiction")

    other_identifiers = relationship("PersonIdentifier", back_populates="person")
    other_names = relationship("PersonName", back_populates="person")
    links = relationship("PersonLink", back_populates="person")
    sources = relationship("PersonSource", back_populates="person")
    offices = relationship("PersonOffice", back_populates="person")

    @property
    def openstates_url(self):
        """get canonical URL for openstates.org"""
        return f"https://openstates.org/person/{slugify(self.name)}-{encode_uuid(self.id)}/"


class PersonIdentifier(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_personidentifier"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    identifier = Column(String)
    scheme = Column(String)


class PersonName(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_personname"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    name = Column(String)
    note = Column(String)


class PersonLink(LinkBase, Base):
    __tablename__ = "opencivicdata_personlink"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)


class PersonSource(LinkBase, Base):
    __tablename__ = "opencivicdata_personsource"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)


class PersonOffice(PrimaryUUID, Base):
    __tablename__ = "openstates_personoffice"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    classification = Column(String)
    address = Column(String)
    voice = Column(String)
    fax = Column(String)
    name = Column(String)


class Membership(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_membership"

    organization_id = Column(String, ForeignKey(Organization.id))
    organization = relationship("Organization")

    person_name = Column(String)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship("Person")

    role = Column(String)
