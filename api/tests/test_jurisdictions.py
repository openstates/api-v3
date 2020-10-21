from .conftest import query_logger


def test_jurisdictions_simplest(client):
    response = client.get("/jurisdictions")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 3
    assert response["results"][0]["name"] == "Mentor"
    assert response["results"][1]["name"] == "Nebraska"
    assert response["results"][2] == {
        "id": "ocd-jurisdiction/country:us/state:oh/government",
        "name": "Ohio",
        "url": "https://ohio.gov",
        "division_id": "ocd-division/country:us/state:oh",
        "classification": "state",
        # note that organizations are not included here as a key
    }


def test_jurisdictions_filter(client):
    response = client.get("/jurisdictions?classification=state")
    response = response.json()
    assert len(response["results"]) == 2
    assert query_logger.count == 2
    response = client.get("/jurisdictions?classification=municipality")
    response = response.json()
    assert len(response["results"]) == 1
    assert query_logger.count == 2


def test_jurisdiction_include_organizations(client):
    response = client.get(
        "/jurisdictions?classification=state&per_page=1&include=organizations"
    )
    response = response.json()
    # is included, organizations are inline
    assert query_logger.count == 4
    assert len(response["results"][0]["organizations"]) == 2
    assert response["results"][0]["organizations"][0] == {
        "id": "nel",
        "classification": "legislature",
        "name": "Nebraska Legislature",
        "districts": [
            {
                "label": "1",
                "division_id": "ocd-division/country:us/state:ne/sldu:1",
                "role": "Senator",
                "maximum_memberships": 1,
            },
        ],
    }


def test_jurisdiction_include_organizations_empty(client):
    response = client.get(
        "/jurisdictions?classification=municipality&per_page=1&include=organizations"
    )
    response = response.json()
    # is included, but the field is empty
    assert len(response["results"][0]["organizations"]) == 0
    assert query_logger.count == 3


def test_jurisdiction_include_sessions(client):
    response = client.get(
        "/jurisdictions?classification=state&per_page=1&include=legislative_sessions"
    )
    response = response.json()
    # is included, legislative sessions are inline
    assert query_logger.count == 3
    assert len(response["results"][0]["legislative_sessions"]) == 2
    assert response["results"][0]["legislative_sessions"][0] == {
        "identifier": "2020",
        "name": "2020",
        "classification": "",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
    }


NEBRASKA_RESPONSE = {
    "id": "ocd-jurisdiction/country:us/state:ne/government",
    "name": "Nebraska",
    "classification": "state",
    "division_id": "ocd-division/country:us/state:ne",
    "url": "https://nebraska.gov",
}


def test_jurisdiction_detail_by_abbr(client):
    response = client.get("/jurisdictions/ne").json()
    assert response == NEBRASKA_RESPONSE
    assert query_logger.count == 1


def test_jurisdiction_detail_by_name(client):
    response = client.get("/jurisdictions/Nebraska").json()
    assert response == NEBRASKA_RESPONSE
    assert query_logger.count == 1


def test_jurisdiction_detail_by_jid(client):
    response = client.get(
        "/jurisdictions/ocd-jurisdiction/country:us/state:ne/government"
    ).json()
    assert response == NEBRASKA_RESPONSE
    assert query_logger.count == 1


def test_jurisdiction_detail_404(client):
    response = client.get("/jurisdictions/xy")
    assert response.status_code == 404
    assert response.json() == {"detail": "No such Jurisdiction."}


def test_jurisdiction_include(client):
    response = client.get("/jurisdictions/ne?include=organizations").json()
    assert len(response["organizations"]) == 2
    assert query_logger.count == 3
