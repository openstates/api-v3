import pytest
from api.db import get_db, models
from api.pagination import Pagination


def test_pagination_basic(client):
    response = client.get("/jurisdictions")
    response = response.json()
    assert response["pagination"] == {
        "page": 1,
        "max_page": 1,
        "per_page": 52,
        "total_items": 3,
    }


def test_pagination_empty(client):
    response = client.get("/people?jurisdiction=wi")
    response = response.json()
    assert response["pagination"] == {
        "page": 1,
        "max_page": 1,
        "per_page": 10,
        "total_items": 0,
    }


def test_pagination_per_page(client):
    response = client.get("/jurisdictions?per_page=2")
    response = response.json()
    assert response["pagination"] == {
        "page": 1,
        "max_page": 2,
        "per_page": 2,
        "total_items": 3,
    }


def test_pagination_page2(client):
    response = client.get("/jurisdictions?per_page=2&page=2")
    response = response.json()
    assert response["results"][0]["name"] == "Ohio"
    assert response["pagination"] == {
        "page": 2,
        "max_page": 2,
        "per_page": 2,
        "total_items": 3,
    }


def test_pagination_invalid_per_page(client):
    response = client.get("/jurisdictions?per_page=0")
    assert response.status_code == 400
    response = response.json()
    assert "invalid per_page" in response["detail"]

    response = client.get("/jurisdictions?per_page=999")
    assert response.status_code == 400
    response = response.json()
    assert "invalid per_page" in response["detail"]


def test_pagination_invalid_page(client):
    response = client.get("/jurisdictions?per_page=2&page=0")
    assert response.status_code == 404
    response = response.json()
    assert "invalid page" in response["detail"]

    response = client.get("/jurisdictions?per_page=2&page=5")
    assert response.status_code == 404
    response = response.json()
    assert "invalid page" in response["detail"]


def test_pagination_no_order_by():
    db = list(get_db())[0]
    query = db.query(models.Jurisdiction)
    p = Pagination()
    with pytest.raises(Exception) as e:
        p.paginate(query)
    assert "ordering is required for pagination" in str(e)
