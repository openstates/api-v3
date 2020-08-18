from fastapi import FastAPI
from . import jurisdictions

app = FastAPI()
app.include_router(jurisdictions.router)
