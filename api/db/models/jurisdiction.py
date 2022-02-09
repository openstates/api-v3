from .. import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
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
    legislative_sessions = relationship(
        "LegislativeSession",
        order_by="LegislativeSession.start_date",
        back_populates="jurisdiction",
    )
    run_plans = relationship(
        "RunPlan", order_by="desc(RunPlan.end_time)", back_populates="jurisdiction"
    )

    def get_latest_runs(self):
        """
        We only want the last <=20 most recent runs
        Run objects look like:
        {
          "success": true,
          "start_time": "2022-02-09T15:13:21.034Z",
          "end_time": "2022-02-09T15:13:21.034Z"
        }
        To get our results, we first ensure the list of run
        objects is sorted by start_time and then end_time (if two objects
        have the same start time), then reverse the order of the
        list to ensure the first 20 items returned are
        the most recent.
        """
        runs = object_session(self).query(RunPlan).with_parent(self)
        return sorted(
            runs, key=lambda i: (i["start_time"], i["end_time"]), reverse=True
        )[:20]


class LegislativeSession(PrimaryUUID, Base):
    __tablename__ = "opencivicdata_legislativesession"

    identifier = Column(String)
    name = Column(String)
    classification = Column(String, default="")
    start_date = Column(String, default="")
    end_date = Column(String, default="")

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")

    downloads = relationship(
        "DataExport",
        back_populates="session",
        primaryjoin="""and_(DataExport.session_id == LegislativeSession.id, DataExport.data_type == 'csv')""",
    )


class DataExport(Base):
    __tablename__ = "bulk_dataexport"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    session_id = Column(UUID(as_uuid=True), ForeignKey(LegislativeSession.id))
    data_type = Column(String)
    url = Column(String)

    session = relationship(LegislativeSession)


class RunPlan(Base):
    __tablename__ = "pupa_runplan"

    id = Column(Integer, primary_key=True, index=True)
    success = Column(Boolean)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    jurisdiction_id = Column(String, ForeignKey(Jurisdiction.id))
    jurisdiction = relationship("Jurisdiction")
