# This script creates a sample Hive alert. Requires a working Hive instance and API key

import requests
import configuration
import random

random.seed(random.randint(1, 1000))
seed = random.random()

headers = {
    'Authorization': 'Bearer %s' % configuration.SYSTEM_SETTINGS['HIVE_API_KEY'],
    'Content-Type': 'application/json',
}

data = '{ "title": "New Alert", "description": "N/A", "type": "external", "source": "instance1", "sourceRef": "%s", "severity": 3 }' % seed

response = requests.post('http://%s:%d/api/alert' % (configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP'], configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']), headers=headers, data=data)

if response == 200:
    print("Successful")
else:
    print(response.text)