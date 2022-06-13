from kafka import KafkaProducer
from kafka import KafkaConsumer

import aerospike
from aerospike import exception as ex

from sup import proc_user_profile, proc_aggregation

import json


consumer = KafkaConsumer('user_tags_test',
                         bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='tag-group'
                         #value_deserializer=lambda x: json.loads(x.decode('utf-8')
                          )



for message in consumer:
    print(message)
    user_tag = json.loads(message)

    proc_user_profile(user_tag)
    proc_aggregation(user_tag)
    #maintain_aerospike(msg['cookie'], msg['action'], msg['primary_key'])
