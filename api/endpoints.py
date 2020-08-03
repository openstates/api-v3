from openstates_metadata import lookup
from openstates.data.models import Person, Jurisdiction
from collections import defaultdict
from .framework import Resource, segment, Endpoint, Parameter


def parse_jurisdiction_param(jid):
    if len(jid) == 2:
        return jid.upper()
    else:
        return lookup(name=jid).abbr


def parse_chamber_param(chamber):
    return chamber


class PersonResource(Resource):
    def __init__(self, obj):
        self.obj = obj

    @segment
    def basic(self):
        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "state": self.obj.current_state,
            "party": self.obj.primary_party,
            "current_role": {
                "chamber": self.obj.current_role["chamber"],
                "district": self.obj.current_role["district"],
                "division_id": self.obj.current_role["division_id"],
                "title": self.obj.current_role["role"],
            },
        }

    @segment
    def extra_bio(self):
        return {
            "family_name": self.obj.family_name,
            "given_name": self.obj.given_name,
            "image": self.obj.image,
            "gender": self.obj.gender,
            "birth_date": self.obj.birth_date,
            "death_date": self.obj.death_date,
            "extras": self.obj.extras,
            "created_at": self.obj.created_at,
            "updated_at": self.obj.updated_at,
        }

    @segment
    def other_identifiers(self):
        return {
            "other_identifiers": [
                {"scheme": oi.scheme, "identifier": oi.identifier}
                for oi in self.obj.identifiers.all()
            ]
        }

    @segment
    def other_names(self):
        return {
            "other_names": [{"name": on.scheme} for on in self.obj.other_names.all()]
        }

    @segment
    def links(self):
        return {"links": [{"url": l.url, "note": l.note} for l in self.obj.links.all()]}

    @segment
    def sources(self):
        return {
            "sources": [{"url": l.url, "note": l.note} for l in self.obj.sources.all()]
        }

    @segment
    def offices(self):
        contact_details = []
        offices = defaultdict(dict)
        for cd in self.obj.contact_details.all():
            offices[cd.note][cd.type] = cd.value
        for office, details in offices.items():
            contact_details.append(
                {
                    "name": office,
                    "fax": None,
                    "voice": None,
                    "email": None,
                    "address": None,
                    **details,
                }
            )
        return {"offices": contact_details}


class JurisdictionResource(Resource):
    def __init__(self, obj):
        self.obj = obj

    @segment
    def basic(self):
        print(self.obj._meta.fields)
        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "url": self.obj.url,
            "classification": self.obj.classification,
        }


class JurisdictionEndpoint(Endpoint):
    parameters = [Parameter("classification", default=None)]
    wrap_resource = JurisdictionResource
    default_per_page = 52
    max_per_page = 100

    def get_results(self, classification, segments):
        jset = Jurisdiction.objects.all().order_by("name")
        if classification:
            jset = jset.filter(classification=classification)
        return jset


class PeopleEndpoint(Endpoint):
    parameters = [
        Parameter("jurisdiction"),
        Parameter("chamber", default=None),
        Parameter("name", default=None),
    ]
    wrap_resource = PersonResource

    def get_results(self, jurisdiction, chamber, name, segments):
        people = (
            Person.objects.exclude(current_role_division_id="")
            .filter(current_state=parse_jurisdiction_param(jurisdiction))
            .order_by("name")
        )

        if name:
            people = people.filter(name__icontains=name)

        if "contact_details" in segments:
            people.prefetch_related("contact_details")

        return people
