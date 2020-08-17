import datetime
from typing import Optional, List
from fastapi import FastAPI
from openstates_metadata import STATES_BY_ABBR
from pydantic import BaseModel
from enum import Enum


class JurisdictionEnum(str, Enum):
    state = "state"
    municipality = "municipality"


class Organization(BaseModel):
    id: str
    name: str
    classification: str


class Jurisdiction(BaseModel):
    id: str
    name: str
    classification: JurisdictionEnum
    division_id: Optional[str]
    url: str
    people_last_updated: datetime.datetime
    bills_last_updated: Optional[datetime.datetime]
    organizations: List[Organization]


app = FastAPI()


def _state_to_dict(s):
    orgs = []
    for org in s.chambers:
        orgs.append(
            Organization(
                name=org.name, id=org.organization_id, classification=org.chamber_type
            )
        )
    orgs.append(
        Organization(
            name=s.executive_name,
            classification="executive",
            id=s.executive_organization_id,
        )
    )

    return {
        "name": s.name,
        "id": s.jurisdiction_id,
        "classification": "state",
        "url": s.url,
        "division_id": s.division_id,
        "people_last_updated": datetime.datetime.utcnow(),
        "bills_last_updated": None,
        "organizations": orgs,
    }


@app.get("/jurisdictions", response_model=List[Jurisdiction])
async def jurisdictions(classification: Optional[JurisdictionEnum] = None):
    return [_state_to_dict(s) for s in STATES_BY_ABBR.values()]
