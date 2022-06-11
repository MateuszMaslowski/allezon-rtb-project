import aerospike
from aerospike import exception as ex


def create_indexes(config):
    client = aerospike.client(config)

    client.connect()

    try:
        client.index_integer_create("mimuw", "view", "cookie", "mimuw_view_cookie_idx")
    except ex.IndexFoundError:
        pass

    try:
        client.index_integer_create("mimuw", "buy", "cookie", "mimuw_buy_cookie_idx")
    except ex.IndexFoundError:
        pass

    try:
        client.index_integer_create("mimuw", "view", "time", "mimuw_view_time_idx")
    except ex.IndexFoundError:
        pass

    try:
        client.index_integer_create("mimuw", "buy", "time", "mimuw_buy_time_idx")
    except ex.IndexFoundError:
        pass

    client.close()
