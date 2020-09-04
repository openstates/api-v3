from .db import models
from openstates_metadata import lookup


def jurisdiction_filter(j: str, *, model):
    if len(j) == 2:
        try:
            return model.jurisdiction_id == lookup(abbr=j).jurisdiction_id
        except KeyError:
            return models.Jurisdiction.name == j
    elif j.startswith("ocd-jurisdiction"):
        return model.jurisdiction_id == j
    else:
        return models.Jurisdiction.name == j
