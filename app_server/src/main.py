from fastapi import FastAPI, Response, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import re
from typing import Union

import hashlib
import json

from get_user_tags import get_user_tags_from_db

from create_indexes import create_indexes

import aerospike
from aerospike import exception as ex
import random

import operator

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

app = FastAPI()


class ProductInfo(BaseModel):
    product_id: str = Field(min_length=1)
    brand_id: str = Field(min_length=1)
    category_id: str = Field(min_length=1)
    price: int = Field(ge=0, lt=1e9)


class UserTags(BaseModel):
    time: str = Field(regex="^(" + utc_date_time_rgx + ")$")
    cookie: str = Field(min_length=1)
    country: str = Field(min_length=1)
    device: str = Field(regex="^(PC|MOBILE|TV)$")
    action: str = Field(regex="^(VIEW|BUY)$")
    origin: str = Field(min_length=1)
    product_info: ProductInfo


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags")
async def add_user_tag(user_tag: UserTags, response: Response):
    if user_tag.action == 'BUY':
        set = 'buy'
    else:
        set = 'view'

    if not client.is_connected():
        client.connect()

    # key = ('mimuw', 'cookies_' + set, user_tag.cookie)

    # try:
    #     (key, metadata, bins) = client.get(key)
    #     no = bins['no']
    #     key = ('mimuw', 'cookies_' + set, user_tag.cookie)
    #     client.put(key, {'no': (no + 1) % 200})
    # except ex.RecordNotFound:
    #     no = 0
    #     client.put(key, {'no': no + 1})

    primary_key = user_tag.cookie + user_tag.time + str(random.randint(1, 10000))

    key = ('mimuw', set, primary_key)

    json = jsonable_encoder(user_tag)
    client.put(key, json)

    response.status_code = 204
    return

#@app.post('/user_profiles/{cookie}?time_range={time_range}')
#async def get_user_tags(cookie : str, time_range : str):
#    response.status_code = 204
#    return

@app.post('/user_profiles/{cookie}')
async def get_user_tags(cookie: str = Query(min_length=1), time_range: str = Query(regex="^(" + time_range_rgx + ")$"), limit : int = 200, response: Response= 200):
    if not client.is_connected():
        client.connect()

    times = re.split('_', time_range)

    print('cipa')
    views = get_user_tags_from_db(client, cookie, 'view', limit, times)
    buys = get_user_tags_from_db(client, cookie, 'buy', limit, times)

    print('chuj')
    response.status_code = 200
    return {"cookie": cookie, "views": views, "buys": buys}


class Dupa(BaseModel):
    cipa: str


@app.post("/user_tags/cipa")
async def cipa(body: Dupa, response: Response):
    response.status_code = 204
    print("View", body)

# curl -X POST -H "Content-Type: application/json" -d '{"time": "2022-03-22T12:15:00.000Z", "cookie": "kuki", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags

# curl -X POST -H "Content-Type: application/json" http://10.112.135.101:8000/user_profiles/kuki?time_range=2022-03-22T12:15:00.000Z_2022-03-22T12:15:00.001Z&limit=20