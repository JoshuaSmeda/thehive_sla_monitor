# Utilities
import json
import time as t
from datetime import datetime
from multiprocessing import Process

# TheHive Imports
from thehive4py.api import TheHiveApi
from thehive4py.query import Eq

# Custom Imports
import configuration
from thehive_sla_monitor.flask import app
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.alerter import Alerter
from thehive_sla_monitor.slack.base import Slack
from thehive_sla_monitor.twilio.base import Twilio
from thehive_sla_monitor.helpers import high_risk_escalate

# Define variables
HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
HIVE_API_KEY = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']
HIVE_API = TheHiveApi("http://%s:%s" % (HIVE_SERVER_IP, HIVE_SERVER_PORT), HIVE_API_KEY)

"""
Define SLA tiers by collecting from configuration.py
"""
LOWSEV = configuration.SLA_SETTINGS['LOW_SEVERITY']
MEDSEV = configuration.SLA_SETTINGS['MEDIUM_SEVERITY']
HIGHSEV = configuration.SLA_SETTINGS['HIGH_SEVERITY']


def severity_switch(i):
    """
    Switch case to pythonically handle severity status for escalations
    """
    switcher = {
        1: 'low_severity',
        2: 'medium_severity',
        3: 'high_severity'
    }
    return switcher.get(i, "Invalid severity selected")


class EscalationSelector:
    """
    Dynamically escalate Hive alerts based on configured severity
    """
    @classmethod
    def escalate(cls, severity, *args, **kwargs):
        """
        This classmethod executes the approriate classmethod based on the providers severity attribute.
        """
        getattr(cls, f'{severity}')(*args, **kwargs)

    @classmethod
    def low_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and sends an SMS to the person currently "on-call".
        """
        logging.warning('LowSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_30_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)
        Twilio().send_sms(*args)

    @classmethod
    def medium_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and makes a call to the person currently "on-call".
        """
        logging.warning('MediumSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_45_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)
        Twilio().make_call(alert_id)

    @classmethod
    def high_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and makes an escalated call once this tier is reached.
        """
        logging.warning('HighSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_60_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)
        Twilio().make_call(alert_id)
        # Twilio Make Escalated Call


def thehive_search(title, query):
    """
    This method queries TheHive for alerts, performs timestamp checks and
    alerts based on the severity tiers reached.
    """
    logging.info("Severity level set to %s. Please ensure this is intended." % configuration.SYSTEM_SETTINGS['SEVERITY_LEVEL'])
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    response = HIVE_API.find_alerts(query=query)

    if response.status_code == 200:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        for element in jdata:
            if high_risk_escalate(element):
                timestamp = int(element['createdAt'])
                timestamp /= 1000
                alert_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
                diff = (current_date - alert_date)
                EscalationSelector.escalate(severity_switch(3), element['id'], element['title'], str(alert_date), str(diff), element)
                Alerter().add_to_60m(element['id'])
            if element['severity'] == configuration.SYSTEM_SETTINGS['SEVERITY_LEVEL']:
                timestamp = int(element['createdAt'])
                timestamp /= 1000
                alert_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                logging.info('Query TheHive found - ID: {id}. Title: {t}. Alert Date: {d}'.format(id=element['id'], t=element['title'], d=str(alert_date)))
                alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
                diff = (current_date - alert_date)

                if LOWSEV < diff.total_seconds() and MEDSEV > diff.total_seconds():
                    logging.warning("Breach: 30/M SLA: " + str(diff) + " " + element['id'])
                    EscalationSelector.escalate(severity_switch(1), element['id'], element['title'], str(alert_date), str(diff), element)
                    Alerter().add_to_30m(element['id'])

                elif MEDSEV < diff.total_seconds() and HIGHSEV > diff.total_seconds():
                    logging.warning("Breach: 45/M SLA: " + str(diff) + " " + element['id'])
                    EscalationSelector.escalate(severity_switch(2), element['id'], element['title'], str(alert_date), str(diff), element)
                    Alerter().add_to_45m(element['id'])

                elif HIGHSEV < diff.total_seconds():
                    logging.warning("Breach: 60/M SLA: " + str(diff) + " " + element['id'])
                    EscalationSelector.escalate(severity_switch(3), element['id'], element['title'], str(alert_date), str(diff), element)
                    Alerter().add_to_60m(element['id'])

        print()

    else:
        logging.error('TheHive: {}/{}'.format(response.status_code, response.text))


def thehive():
    """
    This method queries TheHive API for alerts
    """
    while True:
        try:
            thehive_search('Formatted DATA:', Eq('status', 'New'))
        except Exception as err:
            logging.error("Failure attempting when attempting to escalate TheHive alerts. %s" % err)

        print("Run completed. Re-polling in 2 minutes.")
        t.sleep(20)


def spawn_webserver():
    """
    This method spawns a Flask webserver that's used in conjunction with Slack
    """
    if configuration.FLASK_SETTINGS['ENABLE_WEBSERVER']:
        app.run(port=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT'], host=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'])
    else:
        logging.warning("Flask webserver disabled. You will experience limited functionality.")


if __name__ == '__main__':
    spawn_webserver = Process(target=spawn_webserver)
    thehive = Process(target=thehive)
    thehive.start()
    spawn_webserver.start()
    thehive.join()
    spawn_webserver.join()
