import aerospike
from aerospike import exception as ex

import random

hostIP = '10.112.135.103'
if random.randint(0, 1) == 1:
    hostIP = '10.112.135.104'

config = {
    'hosts': [
        (hostIP, 3000)
    ]
}

write_policies = {'total_timeout': 20000, 'max_retries': 1}
read_policies = {'total_timeout': 15000, 'max_retries': 4}
policies = {'write': write_policies, 'read': read_policies}
config['policies'] = policies

client = aerospike.client(config)
client.connect()


def delete_user_tag(no, action, cookie):
    key = ('mimuw', action + '_indexed', cookie + '_number' + str(no))

    try:
        (key, metadata, bins) = client.get(key)

        primary_key = bins['primary_key']
        key = ('mimuw', action, primary_key)

        client.remove(key)
    except ex.RecordNotFound:
        pass


def maintain_aerospike(cookie, action, primary_key):
    if not client.is_connected():
        client.connect()

    set_number = action + '_number'

    key = ('mimuw', set_number, cookie)

    try:
        (key, metadata, bins) = client.get(key)
        no = bins['no']
        key = ('mimuw', set_number, cookie)
        new_no = (no + 1) % 200
        client.put(key, {'no': new_no})
        delete_user_tag(no, action, cookie)
     except ex.RecordNotFound:
         no = 0
         client.put(key, {'no': 1})

    key = ('mimuw', action + '_indexed', cookie + '_number' + str(no))

    client.put(key, {'primary_key': primary_key})