import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, drop_database, create_database
from sqlalchemy.exc import OperationalError
from fastapi.testclient import TestClient
from api.main import app
from api.auth import apikey_auth
from api.db import Base, get_db
from . import fixtures

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://v3test:v3test@localhost/v3test"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class QueryLogger:
    def __init__(self):
        self.count = 0

    def reset(self):
        self.count = 0

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1
        print(f"==== QUERY #{self.count} ====\n", statement, parameters)


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
    for obj in fixtures.nebraska():
        db.add(obj)
    for obj in fixtures.ohio():
        db.add(obj)
    for obj in fixtures.mentor():
        db.add(obj)
    db.commit()


@pytest.fixture
def client():
    client = TestClient(app)
    return client
