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
from thehive_sla_monitor.flask import app, serve
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
HIGH_ESCALATION_ALERTS = []

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
    """
    To provide flexibility at a later stage - Currently this is in use!
    """
    switcher = {
        1: lambda: Alerter().add_to_alerter_dict(hive_alert['id'], hive_alert['title']),
        2: lambda: Alerter().add_to_alerter_dict(hive_alert['id'], hive_alert['title']),
        3: lambda: Alerter().add_to_alerter_dict(hive_alert['id'], hive_alert['title'])
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
    ACTIVE_SEVERITIES = []
    MAX_AGE = configuration.SYSTEM_SETTINGS['MAX_ALERT_DETECTION_AGE']

    if response.status_code == 200:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        for c in get_active_sla(configuration.SLA_SETTINGS):
            ACTIVE_SEVERITIES.append(c)

        for hive_alert in jdata:
            alert_date, time_diff = get_alert_timer(hive_alert)
            logging.info('[*] TheHive Alert: Title: {t} ({id}). Created at {d}.'.format(id=hive_alert['id'], t=hive_alert['title'], d=str(alert_date)))
            
            # Handle high_risk word escalation
            if high_risk_escalate(hive_alert) and not hive_alert['id'] in HIGH_ESCALATION_ALERTS:
                if MAX_AGE < time_diff.total_seconds() and configuration.SYSTEM_SETTINGS['MAX_ALERT_DETECTION_ENABLED']:
                    pass  # Will catch at line 141
                else:
                    logging.info('HIGH_RISK Severity Breach (%s).' % hive_alert['id'])
                    LOW_SEV, MED_SEV, HIGH_SEV, HIGH_RISK = get_sla_data(configuration.SLA_SETTINGS, severity_switch(hive_alert['severity']))
                    for x in HIGH_RISK['NOTIFICATION_METHOD']:
                        EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)

                    HIGH_ESCALATION_ALERTS.append(hive_alert['id'])

            if hive_alert['id'] not in HIGH_ESCALATION_ALERTS:
                hive_alert_severity = hive_alert['severity']

                if severity_switch(hive_alert_severity) in ACTIVE_SEVERITIES:
                    LOW_SEV, MED_SEV, HIGH_SEV, HIGH_RISK = get_sla_data(configuration.SLA_SETTINGS, severity_switch(hive_alert_severity))

                    if LOW_SEV['TIMER'] < time_diff.total_seconds() and MED_SEV['TIMER'] > time_diff.total_seconds():
                        Alerter().add_to_low_sev(hive_alert['id'])
                        logging.warning('LOW severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        result = any(len(x) >= 3 for x in LOW_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in LOW_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))

                    elif MED_SEV['TIMER'] < time_diff.total_seconds() and HIGH_SEV['TIMER'] > time_diff.total_seconds():
                        Alerter().add_to_med_sev(hive_alert['id'])
                        logging.warning('MEDIUM Severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        result = any(len(x) >= 3 for x in MED_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in MED_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))

                    elif HIGH_SEV['TIMER'] < time_diff.total_seconds() and HIGH_SEV['TIMER'] > time_diff.total_seconds():
                        Alerter().add_to_high_sev(hive_alert['id'])
                        logging.warning('HIGH Severity Breach (%s). Alert Age: %s' % (hive_alert['id'], time_diff))
                        result = any(len(x) >= 3 for x in HIGH_SEV['NOTIFICATION_METHOD'])
                        if result:
                            for x in HIGH_SEV['NOTIFICATION_METHOD']:
                                EscalationSelector.escalate(x, hive_alert['id'], hive_alert['title'], str(alert_date), str(time_diff), hive_alert)
                        else:
                            raise GarbageDataException(severity_switch(hive_alert_severity))

                    elif MAX_AGE < time_diff.total_seconds() and configuration.SYSTEM_SETTINGS['MAX_ALERT_DETECTION_ENABLED']:
                        logging.warning('MAX_AGE Severity Breach (%s). Alert Age: %s. Ignore at own risk!' % (hive_alert['id'], time_diff))
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
        timer = configuration.SYSTEM_SETTINGS['LOOP_TIME']
        thehive_search('Formatted DATA:', Eq('status', 'New'))
        """
        Removed this temporarily since the error handling is poor.
        except Exception as err:
            logging.error("Failure attempting when attempting to escalate TheHive alerts. %s" % err)
        """
        logging.info("Run completed. Re-polling in %s seconds." % timer)
        t.sleep(timer)


def spawn_webserver():
    """
    This method spawns a Flask webserver that's used in conjunction with Slack
    """
    if configuration.FLASK_SETTINGS['ENABLE_WEBSERVER']:
        logging.info("Spawning Waitress webserver.")
        serve(app, host=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'], port=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT'])
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
