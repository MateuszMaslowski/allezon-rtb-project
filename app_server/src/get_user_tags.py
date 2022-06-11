import aerospike


def extract_time(json):
    try:
        return json['time']
    except KeyError:
        return 0


def get_user_tags_from_db(client, cookie, action, limit, times):
    query = client.query('mimuw', action)


    user_tags = query.where(aerospike.predicates.equals('cookie', cookie),
                             aerospike.predicates.between('time', times[0], times[1]))

    return {'chuj': 'dupa'}
    return user_tags

    user_tags.sort(key=extract_time, reverse=True)

    if limit >= len(user_tags):
        return user_tags

    return user_tags[:limit]



