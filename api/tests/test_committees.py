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
