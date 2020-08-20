import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, drop_database, create_database
from sqlalchemy.exc import OperationalError
from fastapi.testclient import TestClient
from api.main import app
from api.auth import apikey_auth
from api.db import Base, get_db
from api.db.models import Jurisdiction, Organization

TEST_DATABASE_URL = "postgresql://v3test:v3test@localhost/v3test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[apikey_auth] = lambda: "disable api key"


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    url = TEST_DATABASE_URL
    try:
        if database_exists(url):
            drop_database(url)
    except OperationalError:
        pass
    create_database(url)
    Base.metadata.create_all(bind=engine)
    yield  # run the tests
    drop_database(url)


@pytest.fixture(scope="session", autouse=True)
def jurisdictions_data():
    db = TestingSessionLocal()
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:ne/government",
        name="Nebraska",
        url="https://nebraska.gov",
        classification="government",
        division_id="ocd-division/country:us/state:ne",
    )
    db.add(Organization(id="abc", name="Nebraska Legislature", classification="legislature", jurisdiction=j))
    db.add(Organization(id="def", name="Nebraska Executive", classification="executive", jurisdiction=j))
    db.add(j)
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/government",
        name="Ohio",
        url="https://ohio.gov",
        classification="government",
        division_id="ocd-division/country:us/state:oh",
    )
    db.add(Organization(id="ghi", name="Ohio Legislature", classification="legislature", jurisdiction=j))
    db.add(Organization(id="jkl", name="Ohio Executive", classification="executive", jurisdiction=j))
    db.add(j)
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/place:mentor",
        name="Mentor",
        url="https://mentoroh.gov",
        classification="municipality",
        division_id="ocd-division/country:us/state:oh/place:mentor",
    )
    db.add(j)
    db.commit()


@pytest.fixture
def client():
    client = TestClient(app)
    return client
