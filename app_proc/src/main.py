from kafka import KafkaConsumer

import aerospike
from aerospike import exception as ex

import json
import random

from time import sleep

from threading import Thread, Lock

import aerospike
from aerospike import exception as ex
from aerospike_helpers.operations import operations as op_helpers

import pandas as pd

from threading import Thread, Lock

buckets = {}

lock = Lock()

hostIP = '10.112.135.103'
if random.randint(0, 1) == 1:
    hostIP = '10.112.135.104'

config = {
    'hosts': [
        (hostIP, 3000)
    ],
    'policy': {
        'key': aerospike.POLICY_KEY_SEND,
        'total_timeout': 100000,
    }
}

write_policies = {'total_timeout': 35000, 'max_retries': 1}
read_policies = {'total_timeout': 20000, 'max_retries': 3}
operate_policies = {'total_timeout': 50000, 'max_retries': 3}
policies = {'write': write_policies, 'read': read_policies, 'operate': operate_policies}
config['policies'] = policies

client = aerospike.client(config)
client.connect()


def extract_time(json_tag):
    try:
        return json_tag['time']
    except KeyError:
        return 0


def proc_user_profile(user_tag):
    key = ('mimuw', 'user_profiles', user_tag['cookie'])

    if user_tag['action'] == 'VIEW':
        actions = 'views'
    else:
        actions = 'buys'

    if not client.is_connected():
        client.connect()

    try:
        _, metadata, bins = client.get(key)
    except ex.RecordNotFound:
        user_profile = {'cookie': user_tag['cookie'], 'views': [], 'buys': []}
        user_profile[actions].append(user_tag)

        if not client.is_connected():
            client.connect()
        client.put(key, {'user_profile': user_profile})
        return

    user_profile = bins['user_profile']

    user_profile[actions].append(user_tag)
    user_profile[actions].sort(key=extract_time, reverse=True)

    if len(user_profile[actions]) > 200:
        user_profile[actions] = user_profile[actions][:200]

    read_gen = metadata['gen']
    write_policy = {'gen': aerospike.POLICY_GEN_EQ}
    ops = [op_helpers.write('user_profile', user_profile),
           op_helpers.read('user_profile')]

    try:
        _, metadata, bins = client.operate(key, ops, meta={'gen': read_gen}, policy=write_policy)
    except ex.RecordGenerationError as e:
        proc_user_profile(user_tag)


def proc_aggregation(user_tag):
    def prep_keys(user_tag):
        # let's start with time
        pref_key = pd.to_datetime(user_tag['time'])
        pref_key = pref_key.strftime("%Y-%m-%dT%H:%M:00")

        pref_key += "?action=" + user_tag['action']
        return [
            pref_key,
            pref_key + "&origin=" + user_tag['origin'],
            pref_key + "&origin=" + user_tag['origin'] + "&brand_id=" + user_tag['product_info']['brand_id'],
            pref_key + "&origin=" + user_tag['origin'] + "&brand_id=" + user_tag['product_info']['brand_id'] + "&category_id=" + user_tag['product_info']['category_id'],
            pref_key + "&origin=" + user_tag['origin'] + "&category_id=" + user_tag['product_info']['category_id'],
            pref_key + "&brand_id=" + user_tag['product_info']['brand_id'],
            pref_key + "&brand_id=" + user_tag['product_info']['brand_id'] + "&category_id=" + user_tag['product_info']['category_id'],
            pref_key + "&category_id=" + user_tag['product_info']['category_id']
        ]

    if not client.is_connected():
        client.connect()

    global buckets, lock

    keys = prep_keys(user_tag)

    lock.acquire()
    for key in keys:
        if key in buckets:
            (count, sum) = buckets[key]
        else:
            (count, sum) = (0, 0)
        buckets[key] = (count + 1, sum + user_tag['product_info']['price'])

    lock.release()


def update_db():
    global lock, buckets
    while True:
        #print('prespanko')
        #sleep(15)
        #print('pospanku')
        lock.acquire()
        if not client.is_connected():
            client.connect()
        for (key, (count, sum)) in buckets.items():
            #print('kluczCHUJ:', key, count, sum)
            client.put(('mimuw', 'aggregate', key), {'count': count, 'sum': sum})
        buckets = {}

        lock.release()


Thread(target=update_db).start()

consumer = KafkaConsumer('user_tags_test',
                         bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='tag-group'
                         #value_deserializer=lambda x: json.loads(x.decode('utf-8')
                          )

#print('hujolbanga')
for message in consumer:
    user_tag = json.loads(message.value)
    #print(user_tag)
    proc_user_profile(user_tag)
    proc_aggregation(user_tag)
    #maintain_aerospike(msg['cookie'], msg['action'], msg['primary_key'])


