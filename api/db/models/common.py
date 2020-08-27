import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID


class PrimaryUUID:
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)


class LinkBase(PrimaryUUID):
    url = Column(String)
    note = Column(String)
