from collections import defaultdict
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .. import Base
from .common import PrimaryUUID, LinkBase
from .jurisdiction import Jurisdiction


class Organization(Base):
    __tablename__ = "opencivicdata_organization"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    classification = Column(String)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")


class Person(Base):
    __tablename__ = "opencivicdata_person"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    family_name = Column(String, default="")
    given_name = Column(String, default="")
    image = Column(String, default="")
    gender = Column(String, default="")
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

    other_identifiers = relationship("PersonIdentifier")
    other_names = relationship("PersonName")
    links = relationship("PersonLink")
    sources = relationship("PersonSource")
    contact_details = relationship("PersonContactDetail")

    @property
    def offices(self):
        """ transform contact details to something more usable """
        contact_details = []
        offices = defaultdict(dict)
        for cd in self.contact_details:
            offices[cd.note][cd.type] = cd.value
        for office, details in offices.items():
            contact_details.append(
                {
                    "name": office,
                    "fax": None,
                    "voice": None,
                    "email": None,
                    "address": None,
                    **details,
                }
            )
        return contact_details


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


class PersonContactDetail(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_personcontactdetail"

    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    type = Column(String)
    value = Column(String)
    note = Column(String)


# TODO: organization_link, organization_source, membership, post
