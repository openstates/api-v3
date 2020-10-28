from .conftest import query_logger
from unittest import mock


def test_by_jurisdiction_abbr(client):
    # by abbr
    response = client.get("/people?jurisdiction=ne").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Boo Berri"


def test_by_jurisdiction_name(client):
    # by name
    response = client.get("/people?jurisdiction=Nebraska").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Boo Berri"


def test_by_jurisdiction_jid(client):
    # by full ID
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
    assert response["results"][0]["gender"] == "female"
    assert response["results"][0]["email"] == "aa@example.com"

    # lower case (also retired)
    response = client.get("/people?name=rita red").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Rita Red"


def test_by_name_other_name(client):
    response = client.get("/people?name=Amy 'Aardvark' Adams").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Amy Adams"


def test_by_id(client):
    response = client.get(
        "/people?id=ocd-person/11111111-1111-1111-1111-111111111111&id=ocd-person/33333333-3333-3333-3333-333333333333"
    ).json()
    assert query_logger.count == 2
    assert len(response["results"]) == 2
    assert response["results"][0]["name"] == "Amy Adams"
    assert response["results"][1]["name"] == "Rita Red"


def test_openstates_url(client):
    response = client.get(
        "/people?id=ocd-person/11111111-1111-1111-1111-111111111111"
    ).json()
    assert query_logger.count == 2
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Amy Adams"
    assert (
        response["results"][0]["openstates_url"]
        == "https://openstates.org/person/amy-adams-WCfTognxqNqfz8qrH12uH/"
    )


def test_no_filter(client):
    response = client.get("/people")
    assert query_logger.count == 0
    assert response.status_code == 400
    assert "is required" in response.json()["detail"]

    response = client.get("/people?org_classification=upper")
    assert query_logger.count == 0
    assert response.status_code == 400
    assert "is required" in response.json()["detail"]


def test_people_includes_normal(client):
    response = client.get(
        "/people?id=ocd-person/11111111-1111-1111-1111-111111111111"
        "&include=other_names&include=other_identifiers&include=links&include=sources"
    ).json()
    assert query_logger.count == 6  # 4 extra queries
    assert response["results"][0]["other_names"] == [
        {"name": "Amy 'Aardvark' Adams", "note": "nickname"}
    ]
    assert response["results"][0]["other_identifiers"] == []  # empty is ok
    assert response["results"][0]["links"] == [
        {"url": "https://example.com/amy", "note": ""}
    ]
    assert response["results"][0]["sources"] == [
        {"url": "https://example.com/amy", "note": ""}
    ]


def test_people_include_office(client):
    response = client.get(
        "/people?id=ocd-person/11111111-1111-1111-1111-111111111111" "&include=offices"
    ).json()
    assert query_logger.count == 3  # 1 extra query
    assert response["results"][0]["offices"] == [
        {"name": "Capitol Office", "address": "123 Main St", "voice": "555-555-5555"}
    ]


def test_people_geo_basic(client):
    with mock.patch("api.people.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "divisions": [
                {
                    "id": "ocd-division/country:us/state:ne/sldu:1",
                    "state": "ne",
                    "name": "1",
                    "division_set": "sldu",
                },
            ]
        }
        response = client.get("/people.geo?lat=41.5&lng=-100").json()
    # 1 query b/c we bypass count() since pagination isn't really needed
    assert query_logger.count == 1
    assert len(response["results"]) == 1
    assert response["results"][0]["name"] == "Amy Adams"
    # check this since skip_count=True was used
    assert response["pagination"]["total_items"] == 1


def test_people_geo_bad_param(client):
    # missing parameter
    with mock.patch("api.people.requests.get") as mock_get:
        response = client.get("/people.geo?lat=38")
        assert response.status_code == 422
        assert response.json()
        assert query_logger.count == 0
        assert mock_get.called is False

    # non-float param
    with mock.patch("api.people.requests.get") as mock_get:
        response = client.get("/people.geo?lat=38&lng=abc")
        assert response.status_code == 422
        assert response.json()
        assert query_logger.count == 0
        assert mock_get.called is False


def test_people_geo_bad_upstream(client):
    # unexpected response from upstream
    with mock.patch("api.people.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"endpoint disabled": True}
        response = client.get("/people.geo?lat=50&lng=50")
        assert response.status_code == 500
        assert response.json()
        assert query_logger.count == 0
        assert mock_get.called is True


def test_people_geo_empty(client):
    with mock.patch("api.people.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"divisions": []}
        response = client.get("/people.geo?lat=0&lng=0")
        assert response.json() == {
            "results": [],
            "pagination": {"max_page": 1, "per_page": 100, "page": 1, "total_items": 0},
        }
        assert query_logger.count == 0
        assert mock_get.called is True
