import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from enum import Enum
from db import SessionLocal, models
from sqlalchemy.orm import joinedload


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class JurisdictionEnum(str, Enum):
    state = "state"
    municipality = "municipality"
    government = "government"


class Organization(BaseModel):
    id: str
    name: str
    classification: str

    class Config:
        orm_mode = True


class Jurisdiction(BaseModel):
    id: str
    name: str
    classification: JurisdictionEnum
    division_id: Optional[str]
    url: str
    # TODO: add these
    # people_last_updated: Optional[datetime.datetime]
    # bills_last_updated: Optional[datetime.datetime]
    organizations: List[Organization]

    class Config:
        orm_mode = True


app = FastAPI()


@app.get("/jurisdictions", response_model=List[Jurisdiction])
async def jurisdictions(
    classification: Optional[JurisdictionEnum] = None,
    db: SessionLocal = Depends(get_db),
):
    # TODO: remove this conversion once database is updated
    if classification == "state":
        classification = "government"
    query = db.query(models.Jurisdiction).options(
        joinedload(models.Jurisdiction.organizations)
    )
    if classification:
        query = query.filter(models.Jurisdiction.classification == classification)
    results = query.all()
    # TODO: ^this too
    for result in results:
        if result.classification == "government":
            result.classification = "state"
    return results
