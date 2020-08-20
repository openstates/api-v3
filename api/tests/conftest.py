import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, drop_database, create_database
from sqlalchemy.exc import OperationalError
from fastapi.testclient import TestClient
from api.main import app
from api.auth import apikey_auth
from api.db import Base, get_db
from api.db.models import Jurisdiction, Organization, Person

TEST_DATABASE_URL = "postgresql://v3test:v3test@localhost/v3test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class QueryLogger:
    def __init__(self):
        self.count = 0

    def reset(self):
        self.count = 0

    def callback(self, *args):
        self.count += 1


query_logger = QueryLogger()


def get_test_db():
    try:
        db = TestingSessionLocal()
        query_logger.reset()
        event.listen(engine, "after_cursor_execute", query_logger.callback)
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[apikey_auth] = lambda: "disable api key"


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    url = TEST_DATABASE_URL
    print("C")
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
def common_data(create_test_database):
    db = TestingSessionLocal()
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:ne/government",
        name="Nebraska",
        url="https://nebraska.gov",
        classification="government",
        division_id="ocd-division/country:us/state:ne",
    )
    db.add(
        Organization(
            id="nel",
            name="Nebraska Legislature",
            classification="legislature",
            jurisdiction=j,
        )
    )
    db.add(
        Organization(
            id="nee",
            name="Nebraska Executive",
            classification="executive",
            jurisdiction=j,
        )
    )
    db.add(
        Person(
            id="1",
            name="Amy Adams",
            family_name="Amy",
            given_name="Adams",
            gender="female",
            birth_date="2000-01-01",
            party="Democratic",
            current_role={
                "org_classification": "legislature",
                "district": 1,
                "title": "Senator",
                "division_id": "ocd-division/country:us/state:ne/sldu:1",
            },
            jurisdiction_id=j.id,
        )
    )
    db.add(
        Person(
            id="2",
            name="Boo Berri",
            birth_date="1973-12-25",
            party="Libertarian",
            current_role={"org_classification": "executive", "title": "Governor"},
            jurisdiction_id=j.id,
        )
    )
    db.add(
        Person(
            id="3",
            name="Rita Red",  # retired
            birth_date="1973-12-25",
            party="Republican",
            jurisdiction_id=j.id,
        )
    )
    db.add(j)
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/government",
        name="Ohio",
        url="https://ohio.gov",
        classification="government",
        division_id="ocd-division/country:us/state:oh",
    )
    db.add(
        Organization(
            id="ohl",
            name="Ohio Legislature",
            classification="legislature",
            jurisdiction=j,
        )
    )
    db.add(
        Organization(
            id="ohe", name="Ohio Executive", classification="executive", jurisdiction=j
        )
    )
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
