from sqlalchemy import and_
from .db import models
from openstates.metadata import lookup


def jurisdiction_filter(j: str, *, jid_field):
    # check either by Jurisdiction.name or a specified field's jurisdiction_id
    if len(j) == 2:
        try:
            return jid_field == lookup(abbr=j).jurisdiction_id
        except KeyError:
            return and_(
                models.Jurisdiction.name == j,
                models.Jurisdiction.classification == "state",
            )
    elif j.startswith("ocd-jurisdiction"):
        return jid_field == j
    else:
        return and_(
            models.Jurisdiction.name == j, models.Jurisdiction.classification == "state"
        )
