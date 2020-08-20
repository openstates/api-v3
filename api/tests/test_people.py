from .conftest import query_logger


def test_by_jurisdiction(client):
    response = client.get("/people?jurisdiction=ne").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Boo Berri"
    response = client.get("/people?jurisdiction=Nebraska").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Boo Berri"

    response = client.get(
        "/people?jurisdiction=ocd-jurisdiction/country:us/state:ne/government"
    ).json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Boo Berri"


def test_by_jurisdiction_and_org_classification(client):
    response = client.get(
        "/people?jurisdiction=ne&org_classification=legislature"
    ).json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Amy Adams"

    response = client.get("/people?jurisdiction=ne&org_classification=executive").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Boo Berri"
    response = client.get("/people?jurisdiction=ne&org_classification=lower").json()
    assert len(response["results"]) == 0


def test_by_name(client):
    response = client.get("/people?name=Amy Adams").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Amy Adams"

    # lower case (also retired)
    response = client.get("/people?name=rita red").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Rita Red"


# TODO: test alternate names and IDs


def test_by_id(client):
    response = client.get("/people?id=1&id=3").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Rita Red"


def test_no_filter(client):
    response = client.get("/people")
    assert query_logger.count == 0
    assert response.status_code == 400
    assert "is required" in response.json()["detail"]

    response = client.get("/people?org_classification=upper")
    assert query_logger.count == 0
    assert response.status_code == 400
    assert "is required" in response.json()["detail"]
