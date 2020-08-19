from typing import Optional
from fastapi import Header, HTTPException


async def apikey_auth(
    apikey: Optional[str] = None, x_apikey: Optional[str] = Header(None)
):
    valid_apikey = x_apikey or apikey
    if not valid_apikey:
        raise HTTPException(
            403,
            detail="Must provide API Key as ?apikey or X-APIKEY. "
            "Login and visit https://openstates.org/account/profile/ for your API key.",
        )
    yield valid_apikey
    # TODO: do API usage update here
