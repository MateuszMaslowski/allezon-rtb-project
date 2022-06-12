from kafka import KafkaProducer
from kafka import KafkaConsumer

import aerospike
from aerospike import exception as ex

from sup import maintain_aerospike

import json

consumer = KafkaConsumer('cookie',
                         bootstrap_servers=['10.112.135.105:9092', '10.112.135.106:9092', '10.112.135.107:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='cookie-group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                         )

for message in consumer:
    maintain_aerospike(message.value['cookie'], message.value['action'], message.value['primary_key'])
