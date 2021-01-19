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
from thehive_sla_monitor.helpers import high_risk_escalate, get_active_sla, get_sla_data, get_alert_timer

# Define variables
HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
HIVE_API_KEY = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']
HIVE_API = TheHiveApi("http://%s:%s" % (HIVE_SERVER_IP, HIVE_SERVER_PORT), HIVE_API_KEY)


def severity_switch(i):
    """
    Switch case to pythonically handle severity status for escalations
    """
    switcher = {
        1: 'THEHIVE_LEVEL1',
        2: 'THEHIVE_LEVEL2',
        3: 'THEHIVE_LEVEL3'
    }
    return switcher.get(i, "Invalid severity selected")


def severity_check(number, hive_alert):
    switcher = {
        1: lambda: Alerter().add_to_low_sev_dict(hive_alert['id'], hive_alert['title']),
        2: lambda: Alerter().add_to_med_sev_dict(hive_alert['id'], hive_alert['title']),
        3: lambda: Alerter().add_to_high_sev_dict(hive_alert['id'], hive_alert['title'])
    }

    return switcher.get(number, lambda: "Invalid severity selected")()

class EscalationSelector:
    """
    Dynamically escalate Hive alerts based on configured severity
    """
    @classmethod
    def escalate(cls, alert_type, *args, **kwargs):
        getattr(cls, f'{alert_type}')(*args, **kwargs)

    @classmethod
    def SLACK_API(cls, alert_id, alert_title, alert_date, alert_age, hive_alert, *args, **kwargs):
        severity_check(hive_alert['severity'], hive_alert)
        Slack().post_notice(alert_id, alert_title, alert_date, alert_age)

    @classmethod
    def TWILIO_SMS(cls, alert_id, alert_title, alert_date, alert_age, hive_alert, *args, **kwargs):
        severity_check(hive_alert['severity'], hive_alert)
        Twilio().send_sms(hive_alert, *args)

    @classmethod
    def TWILIO_CALL(cls, alert_id, alert_title, alert_date, alert_age, hive_alert, *args, **kwargs):
        severity_check(hive_alert['severity'], hive_alert)
        Twilio().make_call(alert_id)


def thehive_search(title, query):
    """
    This method queries TheHive for alerts, performs timestamp checks and
    alerts based on the severity tiers reached.
    """
    response = HIVE_API.find_alerts(query=query)
    high_escalation_alerts = []
    active_severities = []

    if response.status_code == 200:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        for i in get_active_sla(configuration.SLA_SETTINGS):
            active_severities.append(i)

        for hive_alert in jdata:
            alert_date, time_diff = get_alert_timer(hive_alert)
            logging.info('[*] TheHive Alert: Title: {t} ({id}). Created at {d}.'.format(id=hive_alert['id'], t=hive_alert['title'], d=str(alert_date)))
            if high_risk_escalate(hive_alert):
                hive_alert_severity = hive_alert['severity']
                EscalationSelector.escalate(severity_switch(hive_alert_severity), hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                high_escalation_alerts.append(hive_alert['id'])

            if hive_alert['id'] not in high_escalation_alerts:
                hive_alert_severity = hive_alert['severity']

                if severity_switch(hive_alert_severity) in active_severities:
                    LOW_SEV, MED_SEV, HIGH_SEV = get_sla_data(configuration.SLA_SETTINGS, severity_switch(hive_alert_severity))

                    if LOW_SEV['TIMER'] < time_diff.total_seconds() and MED_SEV['TIMER'] > time_diff.total_seconds():
                        logging.warning('LOW severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        Alerter().add_to_low_sev(hive_alert['id'])
                        result = any(len(x) >= 3 for x in LOW_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in LOW_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))
                        Alerter().add_to_low_sev(hive_alert['id'])

                    elif MED_SEV['TIMER'] < time_diff.total_seconds() and HIGH_SEV['TIMER'] > time_diff.total_seconds():
                        logging.warning('MEDIUM severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        Alerter().add_to_med_sev(hive_alert['id'])
                        result = any(len(x) >= 3 for x in MED_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in MED_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))
                        # Alerter().add_to_med_sev(hive_alert['id'])

                    elif HIGH_SEV['TIMER'] < time_diff.total_seconds():
                        logging.warning('HIGH severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        Alerter().add_to_high_sev(hive_alert['id'])
                        result = any(len(x) >= 3 for x in HIGH_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in HIGH_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))
                else:
                    logging.info('%s has a severity level of %s which has not been enabled via configuration.py.' % (hive_alert['id'], hive_alert_severity))
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

        logging.info("Run completed. Re-polling in 2 minutes.")
        t.sleep(10)


def spawn_webserver():
    """
    This method spawns a Flask webserver that's used in conjunction with Slack
    """
    if configuration.FLASK_SETTINGS['ENABLE_WEBSERVER']:
        app.run(port=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT'], host=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'])
    else:
        logging.warning("Flask webserver disabled. You will experience limited functionality.")


class GarbageDataException(Exception):
    def __init__(self, sla_level):
        self.sla_level = sla_level

    def __str__(self):
        logging.error('Potentially garbage notification method in %s configuration. Please review!' % (self.sla_level))
        return 'Error logged, please review and address immediately!'


if __name__ == '__main__':
    spawn_webserver = Process(target=spawn_webserver)
    thehive = Process(target=thehive)
    thehive.start()
    spawn_webserver.start()
    thehive.join()
    spawn_webserver.join()
