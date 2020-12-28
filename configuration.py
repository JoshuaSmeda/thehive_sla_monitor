# Defined SLA Limits in int: seconds

SLA_SETTINGS = {
    '30M': 1800,
    '45M': 2700,
    '60M': 3600
}

SYSTEM_SETTINGS = {
    'HIVE_SERVER_IP': '192.168.1.15',
    'HIVE_SERVER_PORT': 9000,
    'HIVE_FQDN': 'http://192.168.1.15',
    'HIVE_API_KEY' : 'iIMm25V63IjkoLN0MlsJJTcdrPYYhyBi',
    'LOG_FILE_LOCATION': 'thehive_sla_monitor.log'
}

FLASK_SETTINGS = {
    'ENABLE_WEBSERVER': False,
    'FLASK_WEBSERVER_IP': '192.168.1.2',
    'FLASK_WEBSERVER_PORT': 3000
}

TWILIO_SETTINGS = {
    'TWILIO_SENDER': '+000000000',
    'TWILIO_RTCP': '+0000000000',
    'ACCOUNT_SID': 'Aagiant0105101501551',
    'AUTH_TOKEN': '21510515mlagagotg',
    'TWIMLET_URL': 'http://twimlet.domain.com'
}

SLACK_SETTINGS = {
    'SLACK_APP_TOKEN': 'test',
    'SLACK_CHANNEL' : 'test',
    'SLACK_WEBHOOK_URL': 'test'
}