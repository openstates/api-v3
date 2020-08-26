from collections import defaultdict
from . import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
from sqlalchemy.orm import relationship


class Jurisdiction(Base):
    __tablename__ = "opencivicdata_jurisdiction"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    classification = Column(String, index=True)
    division_id = Column(String)

    organizations = relationship(
        "Organization",
        primaryjoin="""and_(
        Jurisdiction.id == Organization.jurisdiction_id,
        Organization.classification.in_(('upper', 'lower', 'legislature', 'executive'))
        )""",
    )


class LegislativeSession(Base):
    __tablename__ = "opencivicdata_legislativesession"

    id = Column(UUID, primary_key=True, index=True)
    identifier = Column(String)
    name = Column(String)
    classification = Column(String)
    start_date = Column(String)
    end_date = Column(String)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")


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
    family_name = Column(String)
    given_name = Column(String)
    image = Column(String)
    gender = Column(String)
    biography = Column(String)
    birth_date = Column(String)
    death_date = Column(String)
    party = Column("primary_party", String)
    current_role = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    extras = Column(JSONB)
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


class PersonIdentifier(Base):
    __tablename__ = "opencivicdata_personidentifier"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    identifier = Column(String)
    scheme = Column(String)


class PersonName(Base):
    __tablename__ = "opencivicdata_personname"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    name = Column(String)
    note = Column(String)


class PersonLink(Base):
    __tablename__ = "opencivicdata_personlink"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    url = Column(String)
    note = Column(String)


class PersonSource(Base):
    __tablename__ = "opencivicdata_personsource"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    url = Column(String)
    note = Column(String)


class PersonContactDetail(Base):
    __tablename__ = "opencivicdata_personcontactdetail"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, ForeignKey(Person.id))
    person = relationship(Person)
    type = Column(String)
    value = Column(String)
    note = Column(String)
    # TODO: label?


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
