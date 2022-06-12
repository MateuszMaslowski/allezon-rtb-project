from fastapi import FastAPI, Response, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from get_user_tags import get_user_tags_from_db
from create_indexes import create_indexes
from post_classes import ProductInfo, UserTags, AggregateQuery

import aerospike
from aerospike import exception as ex

from kafka import KafkaProducer
from kafka import KafkaConsumer

import operator
import re
import random
import hashlib
import json

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
read_policies = {'total_timeout': 1500, 'max_retries': 4}
policies = {'write': write_policies, 'read': read_policies}
config['policies'] = policies

# print(client.is_connected())
client = aerospike.client(config)
client.connect()

# create_indexes(client)

producer = KafkaProducer(bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags")
async def chuj_w_dupe(user_tag: UserTags, response: Response):
    print('CHUJ', user_tag)
    response.status_code = 204
    return


@app.post("/chuj_user_tag")
async def add_user_tag(user_tag: UserTags, response: Response):
    if user_tag.action == 'BUY':
        set = 'buy'
    else:
        set = 'view'

    if not client.is_connected():
        client.connect()

    user_tag_json = jsonable_encoder(user_tag)

    primary_key = json.dumps(user_tag_json, sort_keys=True).encode("utf-8")
    primary_key = hashlib.md5(primary_key).hexdigest()

    key = ('mimuw', set, primary_key)

    client.put(key, user_tag_json)

    producer.send('cookie', value={'cookie': cookie, 'action': action, 'primary_key': primary_key})

    response.status_code = 204
    return


@app.post('/user_profiles/{cookie}')
async def get_user_tags(cookie: str = Query(min_length=1), time_range: str = Query(regex="^(" + time_range_rgx + ")$"), limit : int = 200, response: Response= 200):
    if not client.is_connected():
        client.connect()

    times = re.split('_', time_range)

    views = get_user_tags_from_db(client, cookie, 'view', limit, times)
    buys = get_user_tags_from_db(client, cookie, 'buy', limit, times)

    response.status_code = 200
    return {"cookie": cookie, "views": views, "buys": buys}


@app.post('/aggregates')
async def get_aggregates(aggregate_query: AggregateQuery, response: Response = 200):
    # TODO: Kafka
    response.status_code = 200
    return # TODO: add return

# curl -X POST -H "Content-Type: application/json" -d '{"time": "2022-03-22T12:15:00.000Z", "cookie": "kuki", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags

# curl -X POST -H "Content-Type: application/json" http://10.112.135.101:8000/user_profiles/kuki?time_range=2022-03-22T12:15:00.000_2022-03-22T12:15:00.001&limit=20