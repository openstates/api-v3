from .conftest import query_logger


def test_events_list(client):
    response = client.get("/events?jurisdiction=ne").json()
    assert query_logger.count == 2
    assert len(response["results"]) == 3
    assert response["results"][0]["name"] == "Event #0"
    assert "links" not in response["results"][0]
    assert "sources" not in response["results"][0]


def test_events_list_simple_includes(client):
    response = client.get(
        "/events?jurisdiction=ne&include=sources&include=links"
    ).json()
    # no extra queries for these
    assert query_logger.count == 2
    assert len(response["results"]) == 3
    assert response["results"][0]["name"] == "Event #0"
    assert response["results"][0]["links"][0]["url"] == "https://example.com/0"
    assert response["results"][0]["sources"][0]["url"] == "https://example.com/0"


def test_events_list_join_includes(client):
    response = client.get(
        "/events?jurisdiction=ne&include=media&include=documents&include=participants"
    ).json()
    # one extra query each
    assert query_logger.count == 5
    assert len(response["results"]) == 3
    assert response["results"][0]["name"] == "Event #0"
    assert len(response["results"][0]["media"]) == 1
    assert len(response["results"][0]["documents"]) == 2
    assert len(response["results"][0]["participants"]) == 3


def test_events_list_join_agenda(client):
    response = client.get("/events?jurisdiction=ne&include=agenda").json()
    # agenda is 3 extra queries together
    assert query_logger.count == 5
    assert len(response["results"]) == 3
    assert response["results"][0]["name"] == "Event #0"
    assert len(response["results"][0]["agenda"]) == 2
    assert response["results"][0]["agenda"][0]["description"] == "Agenda Item 1"
    assert response["results"][0]["agenda"][0]["order"] == 1
    assert response["results"][0]["agenda"][0]["media"][0]["date"] == "2021-01-01"
    assert response["results"][0]["agenda"][0]["related_entities"] == [
        {"note": "", "name": "HB 1", "entity_type": "bill"}
    ]
    assert response["results"][0]["agenda"][1]["description"] == "Agenda Item 2"


BASIC_EVENT = {
    "all_day": False,
    "classification": "",
    "deleted": False,
    "description": "",
    "end_date": "",
    "id": "ocd-event/00000000-0000-0000-0000-000000000000",
    "jurisdiction": {
        "classification": "state",
        "id": "ocd-jurisdiction/country:us/state:ne/government",
        "name": "Nebraska",
    },
    "location": {"name": "Location #0", "url": ""},
    "name": "Event #0",
    "start_date": "2021-01-01",
    "status": "normal",
    "upstream_id": "",
}


def test_event_by_id(client):
    response = client.get(
        "/events/ocd-event/00000000-0000-0000-0000-000000000000"
    ).json()
    assert query_logger.count == 1
    assert response == BASIC_EVENT
