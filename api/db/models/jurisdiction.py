from .. import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime
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
    run_plans = relationship("RunPlan", order_by="desc(RunPlan.end_time)")

    @property
    def latest_runs(self):
        """ limit run_plans """
        return self.run_plans[:20]


class LegislativeSession(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_legislativesession"

    identifier = Column(String)
    name = Column(String)
    classification = Column(String, default="")
    start_date = Column(String, default="")
    end_date = Column(String, default="")

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")


class RunPlan(Base):
    __tablename__ = "pupa_runplan"

    id = Column(Integer, primary_key=True, index=True)
    success = Column(Boolean)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")
