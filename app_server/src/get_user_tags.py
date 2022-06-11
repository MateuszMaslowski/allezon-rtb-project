import aerospike


def extract_time(json):
    try:
        return json['time']
    except KeyError:
        return 0


def get_user_tags_from_db(client, cookie, action, limit, times):
    query = client.query('mimuw', action)


    query.where(aerospike.predicates.equals('cookie', cookie))

    # aerospike.predicates.between('time', times[0], times[1])

    # (key, meta, user_tags)
    user_tags_extended = query.results()
    return {'chuj': 'dupa'}
    return user_tags

    user_tags.sort(key=extract_time, reverse=True)

    if limit >= len(user_tags):
        return user_tags

    return user_tags[:limit]



