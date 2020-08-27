from .. import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
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
