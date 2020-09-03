from collections import namedtuple
from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm.exc import NoResultFound
from .db import SessionLocal, get_db, models


Limit = namedtuple("Limit", "daily_requests requests_per_second burst_size")
KEY_LIMITS = {
    # "inactive": None,
    # "suspended": None,
    "default": 500,
    "bronze": 5_000,
    "silver": 25_000,
    "gold": 50_000,
    "unlimited": 1_000_000_000,
}
_cache = {}


async def apikey_auth(
    apikey: Optional[str] = None,
    x_api_key: Optional[str] = Header(None),
    db: SessionLocal = Depends(get_db),
):
    provided_apikey = x_api_key or apikey
    if not provided_apikey:
        raise HTTPException(
            403,
            detail="Must provide API Key as ?apikey or X-API-KEY. "
            "Login and visit https://openstates.org/account/profile/ for your API key.",
        )

    try:
        key = (
            db.query(models.Profile)
            .filter(models.Profile.api_key == provided_apikey)
            .one()
        )
        allowed_requests = KEY_LIMITS.get(key.api_tier)
        invalid = not allowed_requests
    except NoResultFound:
        invalid = True

    if invalid:
        raise HTTPException(
            401,
            detail="Invalid API Key. "
            "Login and visit https://openstates.org/account/profile/ for your API key.",
        )

    yield
    # TODO: do API usage update here
