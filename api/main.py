from fastapi import FastAPI
from . import jurisdictions, people

app = FastAPI()
app.include_router(jurisdictions.router)
app.include_router(people.router)
