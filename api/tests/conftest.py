import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from api.main import app
from api.auth import apikey_auth
from api.db import Base, get_db

TEST_DATABASE_URL = "postgresql://test:test@localhost/v3testdb"
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


@pytest.fixture
def client():
    client = TestClient(app)
    return client
