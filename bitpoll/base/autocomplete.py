from __future__ import unicode_literals

from bitpoll.base.models import BitpollUser

RESULT_LIMIT = 10
MIN_LENGTH = 3


def autocomplete_users(term):
    """Autocomplete users.
    
    If we have only one term, we search the fields username (full),
    username (without year prefix), first_name and last_name. For two
    terms we assume it is first_name, last_name. The first term must
    always be MIN_LENGTH long.

    For queries returning more than RESULT_LIMIT entries, entries are
    ignored, except there is a username matching exactly.
    """
    terms = term.strip().lower().split()
    if len(terms) == 0:
        return []
        
    # Always make sure we "autocomplete" a complete match for username
    try:
        exact_user = BitpollUser.objects.get(username=terms[0 ])
        autocomplete_refused = [exact_user]
    except BitpollUser.DoesNotExist:
        autocomplete_refused = []

    if len(terms[0]) < MIN_LENGTH:
        return autocomplete_refused

    if len(terms) == 1:
        users = []
        dups = set()
        _add_nodup('username', terms[0], users, dups)
        _add_nodup("regexp_replace(username, '^([0-9]+|x)', '')", terms[0], users, dups)
        _add_nodup('lower(first_name)', terms[0], users, dups)
        _add_nodup('lower(last_name)', terms[0], users, dups)
        
        if len(users) > RESULT_LIMIT:
            return autocomplete_refused

    else:
        query = ('SELECT * FROM {} '
                 'WHERE lower(first_name) LIKE %s AND lower(last_name) LIKE %s '
                 'LIMIT %s'.format(BitpollUser._meta.db_table))
        params = (terms[0] + '%', terms[1] + '%', RESULT_LIMIT + 1)
        users = list(BitpollUser.objects.raw(query, params=params))
        if len(users) > RESULT_LIMIT:
            return autocomplete_refused

    users.sort(key=_sort_key)
    return users


def _add_nodup(expr, term, users, dups):
    query = 'SELECT * FROM {} WHERE {} LIKE %s LIMIT %s'.format(BitpollUser._meta.db_table, expr)
    params = (term + '%', RESULT_LIMIT + 1)
    special_users = list(BitpollUser.objects.raw(query, params=params))
    
    for user in special_users:
        if user.pk in dups:
            continue
        users.append(user)
        dups.add(user.pk)


def _sort_key(user):
    return (user.first_name, user.last_name, user.username)
