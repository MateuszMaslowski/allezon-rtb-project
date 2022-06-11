import aerospike


def extract_time(json):
    try:
        return json['time']
    except KeyError:
        return 0


def get_user_tags_from_db(client, cookie, action, limit, times):
    query = client.query('mimuw', action)

    query.where(aerospike.predicates.equals('cookie', cookie))

    user_tags_extended = query.results()

    user_tags = [user_tag for (key, meta, user_tag) in user_tags_extended]

    user_tags.sort(key=extract_time, reverse=True)

    l = 0
    n = len(user_tags)
    res = []
    while l < limit and l < n:
        if times[1] < user_tags[l]:
            l += 1
        elif times[0] > user_tags[l]:
            break
        else:
            res.append(user_tags[l])
            l += 1

    return res


