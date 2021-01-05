import configuration
import sys
import json
import uuid
from thehive4py.api import TheHiveApi
from thehive4py.models import Alert, AlertArtifact, CustomFieldHelper

# Define variables
HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
HIVE_API_KEY = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']
api = TheHiveApi("http://%s:%s" % (HIVE_SERVER_IP, HIVE_SERVER_PORT), HIVE_API_KEY)

# Prepare observables
artifacts = [
    AlertArtifact(dataType='ip', data='8.8.8.8'),
    AlertArtifact(dataType='domain', data='google.com'),
    AlertArtifact(dataType='domain', data='pic.png'),
    AlertArtifact(dataType='domain', data='sample.txt', sighted=True, ioc=True)
]

# Prepare custom fields
customFields = CustomFieldHelper()\
    .build()

# Prepare the sample Alert
sourceRef = str(uuid.uuid4())[0:6]
alert = Alert(title='New Alert',
              tlp=3,
              severity=3,
              tags=['TheHive4Py', 'sample'],
              description='N/A',
              type='external',
              source='instance1',
              sourceRef=sourceRef,
              artifacts=artifacts,
              customFields=customFields)

# Create the alert
try:
    response = api.create_alert(alert)

    # Print the JSON response
    print(json.dumps(response.json(), indent=4, sort_keys=True))

except Exception as e:
    print("Alert create error: {}".format(e))

# Exit the program
sys.exit(0)
