from sqlalchemy.orm import joinedload, noload


def joined_or_noload(query, fieldname, segments):
    """ either pre-join or no-load a segment based on whether it has been requested """
    if fieldname in segments:
        query = query.options(joinedload(fieldname))
    else:
        query = query.options(noload(fieldname))
    return query
