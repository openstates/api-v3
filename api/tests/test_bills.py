from .conftest import query_logger


def test_bills_simplest(client):
    response = client.get("/bills?jurisdiction=ne")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 5
