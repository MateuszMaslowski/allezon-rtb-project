from fastapi import FastAPI, Response, HTTPException, Query

from post_classes import ProductInfo, UserTags
from typing import Union
from typing import List

import aerospike
from aerospike import exception as ex

from kafka import KafkaProducer

import pandas as pd
from datetime import timedelta

import json
import random
import re

utc_date_time_rgx = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"

date_time_rgx = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:(\d{2}|\d{2}.\d{3})"
time_range_rgx = date_time_rgx + "_" + date_time_rgx

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

producer = KafkaProducer(bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'])

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags")
async def add_user_tag(user_tag: UserTags, response: Response):
    user_tag_json = {
        'time': user_tag.time,
        'cookie': user_tag.cookie,
        'country': user_tag.country,
        'device': user_tag.device,
        'action': user_tag.action,
        'origin': user_tag.origin,
        'product_info': {
            'product_id': user_tag.product_info.product_id,
            'brand_id': user_tag.product_info.brand_id,
            'category_id': user_tag.product_info.category_id,
            'price': user_tag.product_info.price
        }
    }

    user_tag_str = json.dumps(user_tag_json).encode("utf-8")

    producer.send('test', user_tag_str)

    response.status_code = 204
    return


@app.post('/user_profiles/{cookie}')
async def get_user_profile(cookie: str = Query(min_length=1),
                           time_range: str = Query(regex="^(" + time_range_rgx + ")$"),
                           limit: int = 200,
                           response: Response = 200):
    def trim_time(actions, times, limit):
        print(actions)
        new_actions = []
        for action in actions:
            if times[0] <= action['time'] < times[1]:
                new_actions.append(action)
        if len(new_actions) > limit:
            new_actions = new_actions[:limit]
        return new_actions

    response.status_code = 200
    return {'cookie': 'xd'}

    if not client.is_connected():
        client.connect()

    times = re.split('_', time_range)
    
    try:
        (key, metadata, bins) = client.get(('mimuw', 'user_profiles', cookie))
    except ex.RecordNotFound:
        response.status_code = 200
        print('empty cookie')
        return {'cookie': cookie, 'views': [], 'buys': []}

    user_profile = bins['user_profile']

    print('came here')

    user_profile['views'] = trim_time(user_profile['views'], times, limit)
    user_profile['buys'] = trim_time(user_profile['buys'], times, limit)

    user_profile['cookie'] = cookie

    response.status_code = 200
    return user_profile


@app.post('/aggregates')
async def get_aggregates(time_range: str = Query(regex="^(" + time_range_rgx + ")$"), 
                         action: str = Query(regex="^(VIEW|BUY)$"),
                         origin: Union[str, None] = Query(default=None), 
                         brand_id: Union[str, None] = Query(default=None), 
                         category_id: Union[str, None] = Query(default=None), 
                         aggregates: List[str] = Query(default=None), 
                         response: Response = 200):
    response.status_code = 200
    return {'cookie': 'xd'}

    res = {
        'colums': ["1m_bucket", "action"],
        'rows': []
    }

    default_rows = []

    if not client.is_connected():
        client.connect()

    suf_key = "?action=" + action
    default_rows.append(action)

    if not origin is None:
        pkey_params = "&origin=" + origin
        res['colums'].append("origin")
        default_rows.append(origin)

    if not brand_id is None:
        pkey_params = "&brand_id=" + brand_id
        res['colums'].append("brand_id")
        default_rows.append(brand_id)

    if not category_id is None:
        pkey_params = "&category_id=" + category_id
        res['colums'].append("category_id")
        default_rows.append(category_id)

    times_str = re.split('_', time_range)

    b_time = pd.to_datetime(times_str[0])
    e_time = pd.to_datetime(times_str[1])

    for aggregate in aggregates:
        if aggregate == 'COUNT' or aggregate == 'count' or aggregate == 'Count':
            res['colums'].append('count')
        else:
            res['colums'].append('sum_price')

    while b_time != e_time:
        pref_key = b_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        m_res = [pref_key] + default_rows
        
        try:
            (key, metadata, bins) = client.get(('mimuw', 'aggregate', pref_key + suf_key))

            for aggregate in aggregates:
                if aggregate == 'COUNT' or aggregate == 'count' or aggregate == 'Count':
                    m_res.append(bins['count'])
                else:
                    m_res.append(bins['sum'])
        except ex.RecordNotFound:
            for _ in range(len(aggregates)):
                m_res.append(0)

        res['rows'].append(m_res)

        b_time = b_time + timedelta(minutes=1)

    response.status_code = 200
    return res

# curl -X POST -H "Content-Type: application/json" -d '{"time": "2022-03-22T12:15:00.000Z", "cookie": "kuki2", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags

# curl -X POST -H "Content-Type: application/json" 'http://10.112.135.101:8000/user_profiles/kuki?time_range=2022-03-22T12:15:00.000_2022-03-22T12:15:00.001&limit=20'

# curl -X POST -H "Content-Type: application/json" 'http://10.112.135.101:8000/aggregates?time_range=2022-03-22T12:15:00.000_2022-03-22T12:16:00.000&action=VIEW&aggregates=sum&aggregates=count'

# curl -X POST -H "Content-Type: application/json" 'http://10.112.135.101:8000/user_profiles/XkXWwGM0UqgJQvMndKBO?time_range=2022-03-01T00:00:00.074_2022-03-01T00:00:00.079&limit=200'