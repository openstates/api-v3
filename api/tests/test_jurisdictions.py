def test_jurisdictions_simplest(client, jurisdictions_data):
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
    }


def test_jurisdiction_segment_default(client):
    response = client.get("/jurisdictions?classification=state&per_page=1")
    response = response.json()
    # if the segment isn't included, the fields are None
    assert "organizations" not in response["results"][0]


def test_jurisdiction_segment_organizations(client):
    response = client.get(
        "/jurisdictions?classification=state&per_page=1&segments=organizations"
    )
    response = response.json()
    # segment is included, organizations are inline
    assert len(response["results"][0]["organizations"]) == 4


def test_jurisdiction_segment_organizations_empty(client):
    response = client.get(
        "/jurisdictions?classification=municipality&per_page=1&segments=organizations"
    )
    response = response.json()
    # segment is included, but the field is empty
    assert len(response["results"][0]["organizations"]) == 0
