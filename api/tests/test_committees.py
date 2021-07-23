from .conftest import query_logger

HOUSE_COM_ID = "ocd-organization/11112222-3333-4444-5555-666677778888"
SENATE_COM_ID = "ocd-organization/11112222-3333-4444-5555-666677779999"
SENATE_COM_RESPONSE = {
    "id": SENATE_COM_ID,
    "name": "Senate Committee on Education",
    "classification": "committee",
    "parent_id": "oss",
}
SENATE_MEMBERSHIPS = [
    {
        "person_id": "ocd-person/99999999-9999-9999-9999-999999999999",
        "person_name": "Ruth",
        "role": "Chair",
    },
    {
        "person_id": "ocd-person/77777777-7777-7777-7777-777777777777",
        "person_name": "Marge",
        "role": "Member",
    },
]


def test_committee_detail(client):
    response = client.get("/committees/" + SENATE_COM_ID)
    assert query_logger.count == 1
    response = response.json()
    assert response == SENATE_COM_RESPONSE


def test_committee_detail_include_memberships(client):
    response = client.get("/committees/" + SENATE_COM_ID + "?include=memberships")
    assert query_logger.count == 2
    response = response.json()
    assert response == dict(memberships=SENATE_MEMBERSHIPS, **SENATE_COM_RESPONSE)


def test_committee_list(client):
    response = client.get("/committees?jurisdiction=oh")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 2
    assert "House Committee on Education" == response["results"][0]["name"]
    assert "Senate Committee on Education" == response["results"][1]["name"]


def test_committee_list_empty(client):
    response = client.get("/committees?jurisdiction=nh")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 0


def test_committee_list_with_members(client):
    response = client.get("/committees?jurisdiction=oh&include=memberships")
    assert query_logger.count == 3
    response = response.json()
    assert len(response["results"]) == 2
    assert "House Committee on Education" == response["results"][0]["name"]
    assert response["results"][0]["memberships"] == []
    assert "Senate Committee on Education" == response["results"][1]["name"]
    assert response["results"][1]["memberships"] == SENATE_MEMBERSHIPS
