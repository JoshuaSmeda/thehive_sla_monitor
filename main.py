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
from thehive_sla_monitor.helpers import high_risk_escalate, get_active_sla, get_sla_data

# Define variables
HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
HIVE_API_KEY = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']
HIVE_API = TheHiveApi("http://%s:%s" % (HIVE_SERVER_IP, HIVE_SERVER_PORT), HIVE_API_KEY)

"""
Define SLA tiers by collecting from configuration.py
"""
# needs to move out
# LOWSEV = configuration.SLA_SETTINGS['LOW_SEVERITY']
# MEDSEV = configuration.SLA_SETTINGS['MEDIUM_SEVERITY']
# HIGHSEV = configuration.SLA_SETTINGS['HIGH_SEVERITY']


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
    def Alert_Slack(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and sends an SMS to the person currently "on-call".
        """
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)

    @classmethod
    def Alert_Twilio_SMS(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        Twilio().send_sms(*args)

    @classmethod
    def Alert_Twilio_Call(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        Twilio().make_call(alert_id)

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


def the_hive_mock():
    """
    to get a specifc config configuration
    """
    # l, m, x = get_sla_data(configuration.SLA_SETTINGS, 'THEHIVE_LEVEL1')
    # print(l)
    # print(m)
    # print(x)
    
    # for obj in get_active_sla(configuration.SLA_SETTINGS):
    #    print("Returning configuration for %s" % obj)
    
    #    l, m, x = get_sla_data(configuration.SLA_SETTINGS, obj)
    #    print(l)
    #    print(m)
    #    print(x)

    #    print(temp_func())

def thehive_search(title, query):
    """
    This method queries TheHive for alerts, performs timestamp checks and
    alerts based on the severity tiers reached.
    """
    # logging.info("Severity level set to %s. Please ensure this is intended." % configuration.SYSTEM_SETTINGS['SEVERITY_LEVEL'])
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    response = HIVE_API.find_alerts(query=query)
    high_esc_list = []

    if response.status_code == 200:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        for hive_alert in jdata:
            """
            Immediately escalate if alert contains a word within the bad word list
            """
            if high_risk_escalate(hive_alert):
                timestamp = int(hive_alert['createdAt'])
                timestamp /= 1000
                alert_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
                diff = (current_date - alert_date)
                # EscalationSelector.escalate(severity_switch(3), hive_alert['id'], hive_alert['title'], str(alert_date), str(diff), hive_alert)
                # Alerter().add_to_60m(hive_alert['id'])
                # high_esc_list.append(hive_alert['id'])

            # Normal workflow
            if hive_alert['id'] not in high_esc_list:
                timestamp = int(hive_alert['createdAt'])
                timestamp /= 1000
                alert_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                logging.info('Query TheHive found - ID: {id}. Title: {t}. Alert Date: {d}'.format(id=hive_alert['id'], t=hive_alert['title'], d=str(alert_date)))
                alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
                diff = (current_date - alert_date)

                """
                Determine whether the hive alert is active so we can check against it via this function
                """
                for obj in get_active_sla(configuration.SLA_SETTINGS):
                    print(obj)

                """
                if this active, do checks against the data
                """

                # Tier 1 check:
                l, m, x = get_sla_data(configuration.SLA_SETTINGS, 'THEHIVE_LEVEL1')
                print(l)
#                result = any(len(elem) >= 3 for elem in l)  # Checks to see if there isn't garbage in alerter function
#                if result:
#                    for item in alert_type:
#                        print(item)

                if LOWSEV < diff.total_seconds() and MEDSEV > diff.total_seconds():
                    logging.warning("Breach: 30/M SLA: " + str(diff) + " " + hive_alert['id'])
                    EscalationSelector.escalate(severity_switch(1), hive_alert['id'], hive_alert['title'], str(alert_date), str(diff), hive_alert)
                    Alerter().add_to_30m(hive_alert['id'])

                elif MEDSEV < diff.total_seconds() and HIGHSEV > diff.total_seconds():
                    logging.warning("Breach: 45/M SLA: " + str(diff) + " " + hive_alert['id'])
                    EscalationSelector.escalate(severity_switch(2), hive_alert['id'], hive_alert['title'], str(alert_date), str(diff), hive_alert)
                    Alerter().add_to_45m(hive_alert['id'])

                elif HIGHSEV < diff.total_seconds():
                    logging.warning("Breach: 60/M SLA: " + str(diff) + " " + hive_alert['id'])
                    EscalationSelector.escalate(severity_switch(3), hive_alert['id'], hive_alert['title'], str(alert_date), str(diff), hive_alert)
                    Alerter().add_to_60m(hive_alert['id'])

        print()

    else:
        logging.error('TheHive: {}/{}'.format(response.status_code, response.text))


def thehive():
    """
    This method queries TheHive API for alerts
    """
    while True:
        try:
#            the_hive_mock()
            thehive_search('Formatted DATA:', Eq('status', 'New'))
        except Exception as err:
            logging.error("Failure attempting when attempting to escalate TheHive alerts. %s" % err)

        print("Run completed. Re-polling in 2 minutes.")
        t.sleep(120)


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
