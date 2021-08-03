from .conftest import query_logger

HOUSE_COM_ID = "ocd-organization/11112222-3333-4444-5555-666677778888"
SENATE_COM_ID = "ocd-organization/11112222-3333-4444-5555-666677779999"
SENATE_COM_RESPONSE = {
    "id": SENATE_COM_ID,
    "name": "Senate Committee on Education",
    "classification": "committee",
    "parent_id": "ohs",
    "extras": {},
}
SENATE_MEMBERSHIPS = [
    {
        "person_name": "Ruth",
        "role": "Chair",
        "person": {
            "id": "ocd-person/99999999-9999-9999-9999-999999999999",
            "name": "Ruth",
            "party": "Democratic",
            "current_role": {
                "district": "9",
                "division_id": "ocd-division/country:us/state:oh/sldu:9",
                "org_classification": "upper",
                "title": "Senator",
            },
        },
    },
    {
        "person_name": "Marge",
        "role": "Member",
        "person": {
            "id": "ocd-person/77777777-7777-7777-7777-777777777777",
            "name": "Marge",
            "party": "Democratic",
            "current_role": {
                "district": "7",
                "division_id": "ocd-division/country:us/state:oh/sldu:7",
                "org_classification": "upper",
                "title": "Senator",
            },
        },
    },
]


def test_committee_detail(client):
    response = client.get("/committees/" + SENATE_COM_ID)
    assert query_logger.count == 1
    response = response.json()
    assert response == SENATE_COM_RESPONSE


def test_committee_detail_include_memberships(client):
    response = client.get("/committees/" + SENATE_COM_ID + "?include=memberships")
    assert query_logger.count == 3
    response = response.json()
    assert response == dict(memberships=SENATE_MEMBERSHIPS, **SENATE_COM_RESPONSE)


def test_committee_list(client):
    response = client.get("/committees?jurisdiction=oh")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 3
    assert "House Committee on Education" == response["results"][0]["name"]
    assert "K-5 Education Subcommittee" == response["results"][1]["name"]
    assert "Senate Committee on Education" == response["results"][2]["name"]


def test_committee_list_empty(client):
    response = client.get("/committees?jurisdiction=nh")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 0


def test_committee_list_with_members(client):
    response = client.get("/committees?jurisdiction=oh&include=memberships")
    assert query_logger.count == 4
    response = response.json()
    assert len(response["results"]) == 3
    assert response["results"][0]["memberships"] == []
    assert response["results"][1]["memberships"] == []
    assert "Senate Committee on Education" == response["results"][2]["name"]
    assert response["results"][2]["memberships"] == SENATE_MEMBERSHIPS


def test_committee_list_with_links_sources_extras(client):
    response = client.get("/committees?jurisdiction=oh&include=links&include=sources")
    assert query_logger.count == 2
    response = response.json()
    assert response["results"][0]["links"] == [
        {"url": "https://example.com/education-link", "note": ""}
    ]
    assert response["results"][0]["sources"] == [
        {"url": "https://example.com/education-source", "note": ""}
    ]
    assert response["results"][0]["extras"] == {"example-room": "Room 84"}


def test_committee_list_by_chamber(client):
    response = client.get("/committees?jurisdiction=oh&chamber=upper")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 1
    assert "Senate Committee on Education" == response["results"][0]["name"]


def test_committee_list_by_parent(client):
    response = client.get("/committees?jurisdiction=oh&parent=ohs")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 1
    assert "Senate Committee on Education" == response["results"][0]["name"]


def test_committee_list_by_classification(client):
    response = client.get("/committees?jurisdiction=oh&classification=subcommittee")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 1
    assert "K-5 Education Subcommittee" == response["results"][0]["name"]
