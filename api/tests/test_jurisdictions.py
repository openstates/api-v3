from fastapi.testclient import TestClient
from api.main import app
from api.auth import apikey_auth

client = TestClient(app)

app.dependency_overrides[apikey_auth] = lambda: "disable api key"


def test_jurisdictions_simplest():
    response = client.get("/jurisdictions")
    response = response.json()
    assert response["results"] != []


def test_jurisdiction_segment_default():
    response = client.get("/jurisdictions?classification=state&per_page=1")
    response = response.json()
    # if the segment isn't included, the fields are None
    assert "organizations" not in response["results"][0]


def test_jurisdiction_segment_organizations():
    response = client.get("/jurisdictions?classification=state&per_page=1&segments=organizations")
    response = response.json()
    # segment is included, organizations are inline
    assert len(response["results"][0]["organizations"]) == 4


def test_jurisdiction_segment_organizations_empty():
    response = client.get("/jurisdictions?classification=municipality&per_page=1&segments=organizations")
    response = response.json()
    # segment is included, but the field is empty
    assert len(response["results"][0]["organizations"]) == 0
