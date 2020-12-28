# This script creates a sample Hive alert. Requires a working Hive instance and API key

import requests
import configuration

headers = {
    'Authorization': 'Bearer %s' % configuration.SYSTEM_SETTINGS['HIVE_API_KEY'],
    'Content-Type': 'application/json',
}

data = '{ "title": "New Alert", "description": "N/A", "type": "external", "source": "instance1", "sourceRef": "alert-ref1", "severity": 3 }'

response = requests.post('http://%s:%d/api/alert' % (configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP'], configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']), headers=headers, data=data)

if response == 200:
    print("Successful")
else:
    print(response.text)