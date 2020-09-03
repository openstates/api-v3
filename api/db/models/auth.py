from .. import Base
from sqlalchemy import Column, String


class Profile(Base):
    __tablename__ = "profiles_profile"

    id = Column(String, primary_key=True, index=True)
    api_key = Column(String, index=True)
    api_tier = Column(String)

    # lots of other fields but we just need these for API
