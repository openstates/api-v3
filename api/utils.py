from sqlalchemy.orm import joinedload, noload


def joined_or_noload(query, fieldname, segments, *, dbname=None):
    """ either pre-join or no-load a segment based on whether it has been requested """
    # if dbname is provided, it is used instead of the fieldname
    if fieldname in segments:
        query = query.options(joinedload(dbname or fieldname))
    else:
        query = query.options(noload(dbname or fieldname))
    return query
