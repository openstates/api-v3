from .conftest import query_logger


def test_bills_filter_by_jurisdiction_abbr(client):
    # state short ID lower case
    response = client.get("/bills?jurisdiction=ne")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 7

    # state short ID upper case
    response = client.get("/bills?jurisdiction=NE")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 7


def test_bills_filter_by_jurisdiction_name(client):
    # by full name
    response = client.get("/bills?jurisdiction=Nebraska")
    assert query_logger.count == 2
    response = response.json()
    assert len(response["results"]) == 7


def test_bills_filter_by_jurisdiction_jid(client):
    # by jid
    response = client.get(
        "/bills?jurisdiction=ocd-jurisdiction/country:us/state:ne/government"
    )
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
    response = client.get("/bills?jurisdiction=oh&chamber=upper")
    assert len(response.json()["results"]) == 1
    response = client.get("/bills?jurisdiction=oh&chamber=lower")
    assert len(response.json()["results"]) == 0


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


def test_bills_include_basics(client):
    response = client.get(
        "/bills?jurisdiction=ne&session=2020&include=sponsorships&include=abstracts"
        "&include=other_titles&include=other_identifiers&include=actions&include=sources"
    )
    assert query_logger.count == 8
    assert response.status_code == 200
    for b in response.json()["results"]:
        assert len(b["sponsorships"]) == 2
        assert len(b["abstracts"]) == 0
        assert len(b["other_titles"]) == 0
        assert len(b["other_identifiers"]) == 0
        assert len(b["actions"]) == 5
        assert len(b["sources"]) == 1
        assert "documents" not in b


def test_bills_include_documents_versions(client):
    response = client.get(
        "/bills?jurisdiction=ne&session=2020&include=documents&include=versions"
    )
    assert query_logger.count == 6
    assert response.status_code == 200
    for b in response.json()["results"]:
        assert len(b["documents"]) == 3
        assert len(b["versions"]) == 2
        assert b["versions"][0] == {
            "note": "Version 0",
            "date": "2020",
            "links": [{"media_type": "text/html", "url": "https://example.com/0"}],
        }
        assert "other_titles" not in b


def test_bills_include_votes(client):
    response = client.get("/bills?q=HB1&include=votes")
    assert query_logger.count == 7
    assert response.status_code == 200
    b = response.json()["results"][0]
    assert b["votes"] == [
        {
            "id": "ocd-vote/1",
            "identifier": "Vote on HB1",
            "motion_text": "Floor Vote",
            "motion_classification": [],
            "start_date": "2021-01-01",
            "result": "passed",
            "organization": {
                "id": "ohh",
                "name": "Ohio House",
                "classification": "lower",
            },
            "votes": [
                {"option": "yes", "voter_name": "Bart"},
                {"option": "yes", "voter_name": "Harley"},
                {"option": "no", "voter_name": "Jarvis"},
            ],
            "counts": [{"option": "yes", "value": 2}, {"option": "no", "value": 1}],
            "sources": [],
        },
        {
            "id": "ocd-vote/2",
            "identifier": "Vote on HB1",
            "motion_text": "Floor Vote",
            "motion_classification": [],
            "start_date": "2021-02-01",
            "result": "passed",
            "organization": {
                "id": "ohs",
                "name": "Ohio Senate",
                "classification": "upper",
            },
            "votes": [],
            "counts": [{"option": "yes", "value": 42}, {"option": "no", "value": 0}],
            "sources": [],
        },
    ]


def test_bill_detail_basic(client):
    response = client.get("/bills/oh/2021/HB 1").json()
    assert response["id"] == "ocd-bill/1234"
    assert query_logger.count == 1


def test_bill_detail_404(client):
    response = client.get("/bills/oh/2021/HB 66")
    assert response.status_code == 404
    assert response.json() == {"detail": "No such Bill."}


def test_bill_detail_id_normalization(client):
    response = client.get("/bills/oh/2021/HB1").json()
    assert response["id"] == "ocd-bill/1234"
    assert query_logger.count == 1

    response = client.get("/bills/oh/2021/hb1").json()
    assert response["id"] == "ocd-bill/1234"
    assert query_logger.count == 1


def test_bill_openstates_url(client):
    response = client.get("/bills/oh/2021/HB1").json()
    assert response["openstates_url"] == "https://openstates.org/oh/bills/2021/HB1/"
    assert query_logger.count == 1


def test_bill_detail_includes(client):
    response = client.get("/bills/oh/2021/HB 1?include=votes").json()
    assert response["id"] == "ocd-bill/1234"
    assert len(response["votes"]) == 2
    assert query_logger.count == 6


def test_bill_detail_by_internal_id(client):
    response = client.get("/bills/ocd-bill/1234").json()
    assert response["id"] == "ocd-bill/1234"
    assert response["identifier"] == "HB 1"
    assert query_logger.count == 1


def test_bill_detail_sponsorship_resolution(client):
    response = client.get("/bills/oh/2021/HB 1?include=sponsorships").json()
    assert response["id"] == "ocd-bill/1234"
    assert len(response["sponsorships"]) == 2
    # uses the compact person representation, no more joins
    assert response["sponsorships"][0] == {
        "name": "Ruth",
        "entity_type": "person",
        "classification": "sponsor",
        "primary": True,
        "person": {
            "id": "ocd-person/99999999-9999-9999-9999-999999999999",
            "name": "Ruth",
            "party": "Democratic",
            "current_role": {
                "title": "Senator",
                "org_classification": "upper",
                "district": "9",
                "division_id": "ocd-division/country:us/state:oh/sldu:9",
            },
        },
    }
    assert query_logger.count == 3
