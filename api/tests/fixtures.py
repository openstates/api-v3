import random
import uuid
import datetime
from sqlalchemy import func
from api.db.models import (
    LegislativeSession,
    Jurisdiction,
    Organization,
    Person,
    PersonName,
    PersonLink,
    PersonSource,
    PersonContactDetail,
    Bill,
    BillAction,
    BillSponsorship,
    BillSource,
    BillVersion,
    BillVersionLink,
    BillDocument,
    BillDocumentLink,
    SearchableBill,
)


def create_test_bill(
    session,
    chamber,
    *,
    sponsors=0,
    actions=0,
    votes=0,
    versions=0,
    documents=0,
    sources=0,
    subjects=None,
    identifier=None,
    classification=None,
):
    b = Bill(
        id="ocd-bill/" + str(uuid.uuid4()),
        identifier=identifier or ("Bill " + str(random.randint(1000, 9000))),
        title="Random Bill",
        legislative_session=session,
        from_organization=chamber,
        subject=subjects or [],
        classification=classification or ["bill"],
        extras={},
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        latest_action_date=session.identifier,  # have the actions take place the same year as session
    )
    yield b
    for n in range(sponsors):
        yield BillSponsorship(
            bill=b,
            primary=True,
            classification="sponsor",
            name="Someone",
            entity_type="person",
        )
    for n in range(actions):
        yield BillAction(
            bill=b,
            description="an action took place",
            date=session.identifier,
            organization=chamber,
            order=n,
        )
    for n in range(sources):
        yield BillSource(bill=b, url="https://example.com/source", note="")
    for n in range(versions):
        bv = BillVersion(bill=b, note=f"Version {n}", date="2020")
        yield bv
        yield BillVersionLink(
            version=bv, url=f"https://example.com/{n}", media_type="text/html"
        )
    for n in range(documents):
        bd = BillDocument(bill=b, note=f"Version {n}", date="2020")
        yield bd
        yield BillDocumentLink(
            document=bd, url=f"https://example.com/{n}", media_type="text/html"
        )


def nebraska():
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:ne/government",
        name="Nebraska",
        url="https://nebraska.gov",
        classification="government",
        division_id="ocd-division/country:us/state:ne",
    )
    ls2020 = LegislativeSession(jurisdiction=j, identifier="2020")
    ls2021 = LegislativeSession(jurisdiction=j, identifier="2021")
    leg = Organization(
        id="nel",
        name="Nebraska Legislature",
        classification="legislature",
        jurisdiction=j,
    )
    bills = []
    for n in range(5):
        bills.extend(
            create_test_bill(
                ls2020,
                leg,
                sponsors=2,
                actions=5,
                versions=2,
                documents=3,
                sources=1,
                subjects=["sample"],
            )
        )
    for n in range(2):
        bills.extend(
            create_test_bill(
                ls2021, leg, subjects=["futurism"], classification=["resolution"],
            )
        )

    return [
        j,
        ls2020,
        ls2021,
        leg,
        *bills,
        Organization(
            id="nee",
            name="Nebraska Executive",
            classification="executive",
            jurisdiction=j,
        ),
        Person(
            id="1",
            name="Amy Adams",
            family_name="Amy",
            given_name="Adams",
            gender="female",
            birth_date="2000-01-01",
            party="Democratic",
            current_role={
                "org_classification": "legislature",
                "district": 1,
                "title": "Senator",
                "division_id": "ocd-division/country:us/state:ne/sldu:1",
            },
            jurisdiction_id=j.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        ),
        PersonName(person_id="1", name="Amy 'Aardvark' Adams", note="nickname"),
        PersonLink(person_id="1", url="https://example.com/amy", note=""),
        PersonSource(person_id="1", url="https://example.com/amy", note=""),
        PersonContactDetail(
            person_id="1", type="voice", value="555-555-5555", note="Capitol Office"
        ),
        PersonContactDetail(
            person_id="1", type="email", value="amy@example.com", note="Capitol Office"
        ),
        Person(
            id="2",
            name="Boo Berri",
            birth_date="1973-12-25",
            party="Libertarian",
            current_role={"org_classification": "executive", "title": "Governor"},
            jurisdiction_id=j.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        ),
        Person(
            id="3",
            name="Rita Red",  # retired
            birth_date="1973-12-25",
            party="Republican",
            jurisdiction_id=j.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        ),
    ]


def ohio():
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/government",
        name="Ohio",
        url="https://ohio.gov",
        classification="government",
        division_id="ocd-division/country:us/state:oh",
    )
    ls2021 = LegislativeSession(jurisdiction=j, identifier="2021")
    leg = Organization(
        id="ohl", name="Ohio Legislature", classification="legislature", jurisdiction=j,
    )
    upper = Organization(
        id="ohs", name="Ohio Senate", classification="upper", jurisdiction=j,
    )
    lower = Organization(
        id="ohh", name="Ohio House", classification="lower", jurisdiction=j,
    )
    hb1 = Bill(
        id="ocd-bill/1234",
        identifier="HB 1",
        title="Alphabetization of OHIO Act",
        legislative_session=ls2021,
        from_organization=upper,
        subject=[],
        classification=["bill"],
        extras={},
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        latest_action_date="2021-01-01",
    )
    btext = SearchableBill(
        bill=hb1,
        search_vector=func.to_tsvector(
            "This bill renames Ohio to HIOO, it is a good idea.", config="english"
        ),
    )
    return [
        j,
        leg,
        upper,
        lower,
        ls2021,
        hb1,
        btext,
        Organization(
            id="ohe", name="Ohio Executive", classification="executive", jurisdiction=j
        ),
    ]


def mentor():
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/place:mentor",
        name="Mentor",
        url="https://mentoroh.gov",
        classification="municipality",
        division_id="ocd-division/country:us/state:oh/place:mentor",
    )
    return [j]
