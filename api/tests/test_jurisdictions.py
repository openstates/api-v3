def test_jurisdictions_simplest(client):
    response = client.get("/jurisdictions")
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
    response = client.get("/jurisdictions?classification=municipality")
    response = response.json()
    assert len(response["results"]) == 1


def test_jurisdiction_include_organizations(client):
    response = client.get(
        "/jurisdictions?classification=state&per_page=1&segments=organizations"
    )
    response = response.json()
    # segment is included, organizations are inline
    assert len(response["results"][0]["organizations"]) == 2
    assert response["results"][0]["organizations"][0] == {
        "id": "abc",
        "classification": "legislature",
        "name": "Nebraska Legislature",
    }


def test_jurisdiction_include_organizations_empty(client):
    response = client.get(
        "/jurisdictions?classification=municipality&per_page=1&segments=organizations"
    )
    response = response.json()
    # segment is included, but the field is empty
    assert len(response["results"][0]["organizations"]) == 0
