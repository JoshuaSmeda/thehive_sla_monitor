# This script creates a sample Hive alert. Requires a working Hive instance and API key

import requests
import random
import configuration

random.seed(random.randint(1, 1000))
seed = random.random()
hive_server_ip = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
hive_server_port = int(configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT'])

headers = {
    'Authorization': 'Bearer %s' % configuration.SYSTEM_SETTINGS['HIVE_API_KEY'],
    'Content-Type': 'application/json',
}

data = '{ "title": "New Alert", "description": "N/A", "type": "external", "source": \
        "instance1", "sourceRef": "%s", "severity": 3 }' % seed

response = requests.post('http://%s:%d/api/alert' % (hive_server_ip, hive_server_port), headers=headers, data=data)

if response.status_code == 201:
    print("Hive Alert Successfully Created!")
else:
    print(response.text)
