from fastapi import FastAPI, Response, HTTPException, Query

from post_classes import ProductInfo, UserTags, AggregateQuery

import aerospike
from aerospike import exception as ex

from kafka import KafkaProducer

import pandas as pd
from datetime import timedelta

import json


hostIP = '10.112.135.103'
if random.randint(0, 1) == 1:
    hostIP = '10.112.135.104'

config = {
    'hosts': [
        (hostIP, 3000)
    ]
}

write_policies = {'total_timeout': 2000, 'max_retries': 1}
read_policies = {'total_timeout': 2000, 'max_retries': 2}
policies = {'write': write_policies, 'read': read_policies}
config['policies'] = policies

# print(client.is_connected())
client = aerospike.client(config)
client.connect()

# create_indexes(client)

producer = KafkaProducer(bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'],
                         value_serializer=lambda x:
                         json.dumps(x).encode('utf-8'))

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags")
async def add_user_tag(user_tag: UserTags, response: Response):
    user_tag_json = json.dumps(user_tag).encode("utf-8")

    producer.send('user_tags_test', key=user_tag.cookie, value=user_tag_json)

    response.status_code = 204
    return


@app.post('/user_profiles/{cookie}')
async def get_user_profile(cookie: str = Query(min_length=1),
                           time_range: str = Query(regex="^(" + time_range_rgx + ")$"), limit: int = 200,
                           response: Response = 200):
    if not client.is_connected():
        client.connect()

    times = re.split('_', time_range)

    (key, metadata, bins) = client.get(('mimuw', 'user_profiles', cookie))

    user_profile = bins['user_profile']

    if len(user_profile.views) > limit:
        user_profile.views = user_profile[:limit]

    if len(user_profile.buys) > limit:
        user_profile.buys = user_profile[:limit]

    user_profile['cookie'] = cookie

    response.status_code = 200
    return user_profile


@app.post('/aggregates')
async def get_aggregates(aggregate_query: AggregateQuery, response: Response = 200):
    res = {
        'colums': ["1m_bucket", "action"],
        'rows': []
    }

    default_rows = []

    if not client.is_connected():
        client.connect()

    suf_key = "?action=" + aggregate_query.action
    default_rows.append(aggregate_query.action)

    if not aggregate_query.origin is None:
        pkey_params = "&origin=" + aggregate_query.origin
        res['colums'].append("origin")
        default_rows.append(aggregate_query.origin)

    if not aggregate_query.brand_id is None:
        pkey_params = "&brand_id=" + aggregate_query.brand_id
        res['colums'].append("brand_id")
        default_rows.append(aggregate_query.brand_id)

    if not aggregate_query.category_id is None:
        pkey_params = "&category_id=" + aggregate_query.category_id
        res['colums'].append("category_id")
        default_rows.append(aggregate_query.category_id)

    times_str = re.split('_', aggregate_query.time_range)

    b_time = pd.to_datetime(times_str[0])
    e_time = pd.to_datetime(times_str[1])

    for aggregates in aggregate_query.aggregates:
        if aggregates == 'COUNT' or aggregates == 'count' or aggregates == 'Count':
            res['colums'].append('count')
        else:
            res['colums'].append('sum_price')

    while b_time != e_time:
        pref_key = b_time.strftime("%Y-%m-%dT%H:%M:%S")

        (key, metadata, bins) = client.get(('mimuw', 'aggregate', pref_key + suf_key))

        m_res = [pref_key] + default_rows

        for aggregates in aggregate_query.aggregates:
            if aggregates == 'COUNT' or aggregates == 'count' or aggregates == 'Count':
                m_res.append(bins['count'])
            else:
                m_res.append(bins['sum'])

        res['rows'].append(m_res)

        b_time = b_time + timedelta(minutes=1)

    response.status_code = 200
    return res

# curl -X POST -H "Content-Type: application/json" -d '{"time": "2022-03-22T12:15:00.000Z", "cookie": "kuki", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags

# curl -X POST -H "Content-Type: application/json" http://10.112.135.101:8000/user_profiles/kuki?time_range=2022-03-22T12:15:00.000_2022-03-22T12:15:00.001&limit=20
