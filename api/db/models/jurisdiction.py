from .. import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship, object_session
from .common import PrimaryUUID


class Jurisdiction(Base):
    __tablename__ = "opencivicdata_jurisdiction"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    classification = Column(String, index=True)
    division_id = Column(String)
    latest_bill_update = Column(DateTime)
    latest_people_update = Column(DateTime)

    organizations = relationship(
        "Organization",
        primaryjoin="""and_(
        Jurisdiction.id == Organization.jurisdiction_id,
        Organization.classification.in_(('upper', 'lower', 'legislature', 'executive'))
        )""",
    )
    legislative_sessions = relationship("LegislativeSession")
    run_plans = relationship("RunPlan", order_by="desc(RunPlan.end_time)")

    def get_latest_runs(self):
        return object_session(self).query(RunPlan).with_parent(self)[:20]


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
