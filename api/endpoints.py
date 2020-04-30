# from openstates_metadata import lookup
from openstates.data.models import Person
from collections import defaultdict
from .framework import Resource, segment


def parse_state_param(state):
    return state.upper()


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
                "chamber": self.obj.current_role['chamber'],
                "district": self.obj.current_role['district'],
                "division_id": self.obj.current_role['division_id'],
                "title": self.obj.current_role['role'],
            }
        }

    @segment
    def offices(self):
        contact_details = []
        offices = defaultdict(dict)
        for cd in self.obj.contact_details.all():
            offices[cd.note][cd.type] = cd.value
        for office, details in offices.items():
            contact_details.append({
                "office": office,
                **details
            })
        return {
            "offices": contact_details
        }


def legislators(state, chamber=None, segments=None):
    abbr = parse_state_param(state)
    chamber = parse_chamber_param(chamber)

    people = Person.objects.exclude(current_role_division_id="").filter(
        current_state=abbr
    ).order_by("name")

    if "contact_details" in segments:
        people.prefetch_related("contact_details")

    return [PersonResource(person).as_dict(segments) for person in people]
