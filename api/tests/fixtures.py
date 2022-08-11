import random
import uuid
import datetime
from sqlalchemy import func
from api.db.models import (
    Bill,
    BillAction,
    BillDocument,
    BillDocumentLink,
    BillSource,
    BillSponsorship,
    BillVersion,
    BillVersionLink,
    RelatedBill,
    Event,
    EventAgendaItem,
    EventAgendaMedia,
    EventDocument,
    EventLocation,
    EventMedia,
    EventParticipant,
    EventRelatedEntity,
    Jurisdiction,
    LegislativeSession,
    DataExport,
    Membership,
    Organization,
    Person,
    PersonOffice,
    PersonLink,
    PersonName,
    PersonSource,
    PersonVote,
    Post,
    RunPlan,
    SearchableBill,
    VoteCount,
    VoteEvent,
)


def dummy_person_id(n):
    return f"ocd-person/{n*8}-{n*4}-{n*4}-{n*4}-{n*12}"


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
        latest_action_date=f"{session.identifier}-02-{random.randint(10,30)}",
        first_action_date=f"{session.identifier}-01-{random.randint(10,30)}",
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


def create_test_event(
    jid, n, *, start_date, deleted=False, related_bill=False, related_committee=False
):
    loc = EventLocation(
        id=str(uuid.uuid4()), name=f"Location #{n}", jurisdiction_id=jid, url=""
    )
    e = Event(
        jurisdiction_id=jid,
        id=f"ocd-event/00000000-0000-0000-0000-{n:012d}",
        name=f"Event #{n}",
        description="",
        classification="",
        start_date=start_date,
        end_date="",
        all_day=False,
        status="normal",
        upstream_id="",
        deleted=deleted,
        location=loc,
        links=[{"note": "source", "url": f"https://example.com/{n}"}],
        sources=[{"note": "source", "url": f"https://example.com/{n}"}],
    )
    yield loc
    yield e
    yield EventMedia(
        event=e, note="", date=start_date, offset=0, classification="", links=[],
    )
    yield EventDocument(
        event=e, date=start_date, note="document 1", classification="", links=[],
    )
    yield EventDocument(
        event=e, date=start_date, note="document 2", classification="", links=[],
    )
    yield EventParticipant(
        event=e, note="", name="John", entity_type="person",
    )
    yield EventParticipant(
        event=e, note="", name="Jane", entity_type="person",
    )
    yield EventParticipant(
        event=e, note="", name="Javier", entity_type="person",
    )
    a1 = EventAgendaItem(
        id=str(uuid.uuid4()),
        event=e,
        description="Agenda Item 1",
        classification="",
        subjects=[],
        notes=[],
        extras={},
        order=1,
    )
    yield a1
    yield EventAgendaMedia(
        agenda_item=a1, note="", date=start_date, offset=0, classification="", links=[],
    )
    yield EventAgendaItem(
        id=str(uuid.uuid4()),
        event=e,
        description="Agenda Item 2",
        classification="",
        subjects=[],
        notes=[],
        extras={},
        order=2,
    )
    if related_bill:
        yield EventRelatedEntity(
            agenda_item=a1, note="", name="SB 1", entity_type="bill",
        )
    if related_committee:
        yield EventRelatedEntity(
            agenda_item=a1, note="", name="Finance", entity_type="organization"
        )


def nebraska():
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:ne/government",
        name="Nebraska",
        url="https://nebraska.gov",
        classification="state",
        division_id="ocd-division/country:us/state:ne",
        latest_bill_update=datetime.datetime(2021, 8, 1),
        latest_people_update=datetime.datetime(2021, 8, 2),
    )
    runs = []
    runs_from = datetime.datetime(2020, 1, 1)
    for n in range(100):
        runs.append(
            RunPlan(
                jurisdiction=j,
                start_time=runs_from + datetime.timedelta(days=n),
                end_time=runs_from + datetime.timedelta(days=n, hours=3),
                success=n % 2 == 0,
            )
        )
    ls2020 = LegislativeSession(
        jurisdiction=j,
        identifier="2020",
        name="2020",
        start_date="2020-01-01",
        end_date="2020-12-31",
    )
    data_export = DataExport(
        session=ls2020,
        data_type="csv",
        created_at="2021-01-01",
        updated_at="2021-01-01",
        url="https://example.com",
    )
    ls2021 = LegislativeSession(
        jurisdiction=j, identifier="2021", name="2020", start_date="2021-01-01"
    )
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
                ls2021,
                leg,
                subjects=["futurism"],
                classification=["resolution"],
                identifier=f"SB {n+1}",
            )
        )
    events = []
    for n in range(3):
        events.extend(
            create_test_event(
                j.id,
                n,
                start_date=f"2021-01-0{n+1}",
                related_bill=(n == 0),
                related_committee=(n > 1),
            )
        )
    events.extend(create_test_event(j.id, 4, start_date="2021-01-04", deleted=True))

    return [
        j,
        ls2020,
        data_export,
        ls2021,
        leg,
        *runs,
        *bills,
        *events,
        Organization(
            id="nee",
            name="Nebraska Executive",
            classification="executive",
            jurisdiction=j,
        ),
        Post(
            id="a",
            organization=leg,
            label="1",
            role="Senator",
            maximum_memberships=1,
            division_id="ocd-division/country:us/state:ne/sldu:1",
        ),
        Person(
            id=dummy_person_id("1"),
            name="Amy Adams",
            family_name="Amy",
            given_name="Adams",
            gender="female",
            email="aa@example.com",
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
        PersonName(
            person_id=dummy_person_id("1"), name="Amy 'Aardvark' Adams", note="nickname"
        ),
        PersonLink(
            person_id=dummy_person_id("1"), url="https://example.com/amy", note=""
        ),
        PersonSource(
            person_id=dummy_person_id("1"), url="https://example.com/amy", note=""
        ),
        PersonOffice(
            person_id=dummy_person_id("1"),
            classification="capitol",
            voice="555-555-5555",
            fax="",
            address="123 Main St",
            name_="",
        ),
        Person(
            id=dummy_person_id("2"),
            name="Boo Berri",
            birth_date="1973-12-25",
            party="Libertarian",
            current_role={"org_classification": "executive", "title": "Governor"},
            jurisdiction_id=j.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        ),
        Person(
            id=dummy_person_id("3"),
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
        classification="state",
        division_id="ocd-division/country:us/state:oh",
        latest_bill_update=datetime.datetime(2021, 8, 4),
        latest_people_update=datetime.datetime(2021, 8, 5),
    )
    ls2021 = LegislativeSession(jurisdiction=j, identifier="2021", name="2021")
    leg = Organization(
        id="ohl", name="Ohio Legislature", classification="legislature", jurisdiction=j,
    )
    upper = Organization(
        id="ohs", name="Ohio Senate", classification="upper", jurisdiction=j,
    )
    lower = Organization(
        id="ohh", name="Ohio House", classification="lower", jurisdiction=j,
    )
    house_education = Organization(
        id="ocd-organization/11112222-3333-4444-5555-666677778888",
        jurisdiction=j,
        parent_id="ohh",
        name="House Committee on Education",
        classification="committee",
        links=[{"url": "https://example.com/education-link", "note": ""}],
        sources=[{"url": "https://example.com/education-source", "note": ""}],
        extras={"example-room": "Room 84"},
    )
    senate_education = Organization(
        id="ocd-organization/11112222-3333-4444-5555-666677779999",
        jurisdiction=j,
        parent_id="ohs",
        name="Senate Committee on Education",
        classification="committee",
    )
    k5_sub = Organization(
        id="ocd-organization/11112222-3333-4444-5555-000000000000",
        jurisdiction=j,
        parent_id=house_education.id,
        name="K-5 Education Subcommittee",
        classification="subcommittee",
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
    # sb1 = Bill(
    #     id="ocd-bill/9999",
    #     identifier="SB 1",
    related_bill = RelatedBill(
        bill=hb1,
        identifier="SB 1",
        legislative_session="2021",
        relation_type="companion",
    )
    ruth = Person(
        id=dummy_person_id("9"),
        name="Ruth",
        party="Democratic",
        current_role={
            "org_classification": "upper",
            "district": 9,
            "title": "Senator",
            "division_id": "ocd-division/country:us/state:oh/sldu:9",
        },
    )
    marge = Person(
        id=dummy_person_id("7"),
        name="Marge",
        party="Democratic",
        current_role={
            "org_classification": "upper",
            "district": 7,
            "title": "Senator",
            "division_id": "ocd-division/country:us/state:oh/sldu:7",
        },
    )
    sp1 = BillSponsorship(
        bill=hb1,
        primary=True,
        classification="sponsor",
        name="Ruth",
        entity_type="person",
        person=ruth,
    )
    sp2 = BillSponsorship(
        bill=hb1,
        primary=True,
        classification="cosponsor",
        name="Marge",
        entity_type="person",
        person=marge,
    )
    btext = SearchableBill(
        bill=hb1,
        search_vector=func.to_tsvector(
            "This bill renames Ohio to HIOO, it is a good idea.", config="english"
        ),
    )
    v1 = VoteEvent(
        id="ocd-vote/1",
        bill=hb1,
        identifier="Vote on HB1",
        motion_text="Floor Vote",
        start_date="2021-01-01",
        result="passed",
        organization=lower,
    )
    v2 = VoteEvent(
        id="ocd-vote/2",
        bill=hb1,
        identifier="Vote on HB1",
        motion_text="Floor Vote",
        start_date="2021-02-01",
        result="passed",
        organization=upper,
    )
    com_mem1 = Membership(
        organization_id=senate_education.id,
        person_id=ruth.id,
        role="Chair",
        person_name="Ruth",
    )
    com_mem2 = Membership(
        organization_id=senate_education.id,
        person_id=marge.id,
        role="Member",
        person_name="Marge",
    )
    return [
        j,
        leg,
        upper,
        lower,
        ls2021,
        hb1,
        related_bill,
        ruth,
        marge,
        sp1,
        sp2,
        v1,
        v2,
        VoteCount(vote_event=v1, option="yes", value=2),
        VoteCount(vote_event=v1, option="no", value=1),
        PersonVote(vote_event=v1, option="yes", voter_name="Bart"),
        PersonVote(vote_event=v1, option="yes", voter_name="Harley"),
        PersonVote(vote_event=v1, option="no", voter_name="Jarvis"),
        VoteCount(vote_event=v2, option="yes", value=42),
        VoteCount(vote_event=v2, option="no", value=0),
        btext,
        Organization(
            id="ohe", name="Ohio Executive", classification="executive", jurisdiction=j
        ),
        house_education,
        senate_education,
        k5_sub,
        com_mem1,
        com_mem2,
    ]


def mentor():
    j = Jurisdiction(
        id="ocd-jurisdiction/country:us/state:oh/place:mentor",
        name="Mentor",
        url="https://mentoroh.gov",
        classification="municipality",
        division_id="ocd-division/country:us/state:oh/place:mentor",
        latest_bill_update=datetime.datetime(2021, 8, 1),
        latest_people_update=datetime.datetime(2021, 8, 2),
    )
    return [j]
