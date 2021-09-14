from .. import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime


class Event(Base):
    __tablename__ = "opsencivicdata_event"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    jurisdiction = ColumnString(String)
    description = Column(String)
    classification = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    all_day = Column(Boolean)
    status = Column(String)
