from .. import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .common import PrimaryUUID


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
    legislative_sessions = relationship("LegislativeSession")


class LegislativeSession(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_legislativesession"

    identifier = Column(String)
    name = Column(String)
    classification = Column(String, default="")
    start_date = Column(String, default="")
    end_date = Column(String, default="")

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")
