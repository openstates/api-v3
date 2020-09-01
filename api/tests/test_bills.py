from .conftest import query_logger


def test_bills_filter_by_jurisdiction(client):
    response = client.get("/bills?jurisdiction=ne")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 7


def test_bills_filter_by_session(client):
    # 5 bills are in 2020
    response = client.get("/bills?jurisdiction=ne&session=2020")
    assert query_logger.count == 2
    assert len(response.json()["results"]) == 5


def test_bills_filter_by_chamber(client):
    response = client.get("/bills?jurisdiction=ne&chamber=legislature")
    assert len(response.json()["results"]) == 7
    # TODO: test other chambers


def test_bills_filter_by_classification(client):
    response = client.get("/bills?jurisdiction=ne&classification=bill")
    assert len(response.json()["results"]) == 5
    response = client.get("/bills?jurisdiction=ne&classification=resolution")
    assert len(response.json()["results"]) == 2


def test_bills_filter_by_subject(client):
    response = client.get("/bills?jurisdiction=ne&subject=futurism")
    response = response.json()
    assert len(response["results"]) == 2


def test_bills_filter_by_updated_since(client):
    response = client.get("/bills?jurisdiction=ne&updated_since=2020")
    assert len(response.json()["results"]) == 7
    response = client.get("/bills?jurisdiction=ne&updated_since=2022")
    assert len(response.json()["results"]) == 0


def test_bills_filter_by_action_since(client):
    response = client.get("/bills?jurisdiction=ne&action_since=2020")
    assert len(response.json()["results"]) == 7
    response = client.get("/bills?jurisdiction=ne&action_since=2021")
    assert len(response.json()["results"]) == 2


def test_bills_filter_by_query(client):
    response = client.get("/bills?q=HIOO")
    assert len(response.json()["results"]) == 1
    response = client.get("/bills?q=Ohio")
    assert len(response.json()["results"]) == 1
    response = client.get("/bills?q=Cleveland")
    assert len(response.json()["results"]) == 0


def test_bills_filter_by_query_bill_id(client):
    response = client.get("/bills?q=HB 1")
    assert len(response.json()["results"]) == 1
    response = client.get("/bills?q=hb1")
    assert len(response.json()["results"]) == 1
    response = client.get("/bills?q=hb6")
    assert len(response.json()["results"]) == 0


def test_bills_no_filter(client):
    response = client.get("/bills")
    assert query_logger.count == 0
    assert response.status_code == 400
    assert "required" in response.json()["detail"]
