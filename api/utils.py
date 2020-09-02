from sqlalchemy.orm import noload, selectinload


def joined_or_noload(query, fieldname, all_includes, *, dbname=None):
    """ either pre-join or no-load data based on whether it has been requested """
    # if dbname is provided, it is used instead of the fieldname
    if fieldname in all_includes:
        # selectinload seems like a strong default choice, but it is possible that
        # some configurability might be desirable eventually for some types of data
        query = query.options(selectinload(dbname or fieldname))
    else:
        query = query.options(noload(dbname or fieldname))
    return query
