from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm.exc import NoResultFound
from rrl import RateLimiter, Tier, RateLimitExceeded
from .db import SessionLocal, get_db, models

limiter = RateLimiter(
    prefix="v3",
    tiers=[
        Tier("default", 10, 0, 500),
        Tier("legacy", 40, 0, 5000),  # legacy v1 tier -- same as bronze for us
        Tier("bronze", 40, 0, 5000),
        Tier("silver", 80, 0, 50000),
        Tier("unlimited", 240, 0, 1_000_000_000),
    ],
    use_redis_time=False,
    track_daily_usage=True,
)


def apikey_auth(
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
        try:
            limiter.check_limit(provided_apikey, key.api_tier)
        except RateLimitExceeded as e:
            raise HTTPException(429, detail=str(e))
        except ValueError:
            raise HTTPException(
                401,
                detail="Inactive API Key. "
                "Login and visit https://openstates.org/account/profile/ for details.",
            )
    except NoResultFound:
        raise HTTPException(
            401,
            detail="Invalid API Key. "
            "Login and visit https://openstates.org/account/profile/ for your API key.",
        )
