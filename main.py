# Utilities
import json
import time as t
from datetime import datetime, time
from multiprocessing import Process

# TheHive Imports
from thehive4py.api import TheHiveApi
from thehive4py.query import *

# Custom Imports
import configuration
from thehive_sla_monitor.flask import *
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.alerter import Alerter
from thehive_sla_monitor.slack.base import Slack

# Define variables
hive_server_ip = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
hive_server_port = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
hive_api_key = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']

hive_API = TheHiveApi("http://%s:%s" % (hive_server_ip, hive_server_port), hive_api_key)

"""
Define SLA tiers by collecting from configuration.py
"""

sla_30 = configuration.SLA_SETTINGS['LOW_SEVERITY']
sla_45 = configuration.SLA_SETTINGS['MEDIUM_SEVERITY']
sla_60 = configuration.SLA_SETTINGS['HIGH_SEVERITY']


def severity_switch(i):
    """
    Switch case to pythonically handle severity status for escalations
    """
    switcher = {
        1: 'LowSeverity',
        2: 'MediumSeverity',
        3: 'HighSeverity'
    }
    return switcher.get(i, "Invalid severity selected")


class EscalationSelector:
    """
    Dynamically escalate Hive alerts based on configured severity
    """
    @classmethod
    def escalate(cls, severity, *args, **kwargs):
        getattr(cls, f'{severity}')(*args, **kwargs)

    @classmethod
    def LowSeverity(cls, id, rule_name, alert_date, alert_age, *args, **kwargs):
        logging.warning('LowSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (id, rule_name, alert_date, alert_age))
        Alerter().add_to_30_dict(id, rule_name)
        Slack().post_notice(id, rule_name, alert_date, alert_age)

        # send_sms(*args)

    @classmethod
    def MediumSeverity(cls, id, rule_name, alert_date, alert_age, *args, **kwargs):
        logging.warning('MediumSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (id, rule_name, alert_date, alert_age))
        Alerter().add_to_45_dict(id, rule_name)
        Slack().post_notice(id, rule_name, alert_date, alert_age)
        # slack_bot_notice_alert(channel, id, rule_name, alert_date, alert_age)
        # make_call(id)

    @classmethod
    def HighSeverity(cls, id, rule_name, alert_date, alert_age, *args, **kwargs):
        logging.warning('HighSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (id, rule_name, alert_date, alert_age))
        Alerter().add_to_60_dict(id, rule_name)
        Slack().post_notice(id, rule_name, alert_date, alert_age)
        # make_escalated_call(id)


def thehive_search(title, query):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    response = hive_API.find_alerts(query=query)

    if response.status_code == 200:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        for d in jdata:
            if d['severity'] == 3:
                ts = int(d['createdAt'])
                ts /= 1000
                alert_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                logging.info('Searching TheHive found ID: {id}. Title: {t}. Alert Date: {d}'.format(id=d['id'], t=d['title'], d=str(alert_date)))
                alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
                diff = (current_date - alert_date)

                if sla_30 < diff.total_seconds() and sla_45 > diff.total_seconds():
                    logging.warning("Breach: 30/M SLA: " + str(diff) + " " + d['id'])
                    EscalationSelector.escalate(severity_switch(1), d['id'], d['title'], str(alert_date), str(diff), d)
                    Alerter().add_to_30m(d['id'])

                elif sla_45 < diff.total_seconds() and sla_60 > diff.total_seconds():
                    logging.warning("Breach: 45/M SLA: " + str(diff) + " " + d['id'])
                    EscalationSelector.escalate(severity_switch(2), d['id'], d['title'], str(alert_date), str(diff), d)
                    Alerter().add_to_45m(d['id'])

                elif sla_60 < diff.total_seconds():
                    logging.warning("Breach: 60/M SLA: " + str(diff) + " " + d['id'])
                    EscalationSelector.escalate(severity_switch(3), d['id'], d['title'], str(alert_date), str(diff), d)
                    Alerter().add_to_60m(d['id'])

        print()

    else:
        logging.error('TheHive: {}/{}'.format(response.status_code, response.text))


def promote_to_case(case_id):
    logging.info("Promoting Alert %s" % case_id)
    response = hive_API.promote_alert_to_case(case_id)
    if response.status_code == 201:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        case_id = (jdata['id'])
        return case_id
    else:
        logging.error('TheHive: {}/{}'.format(response.status_code, response.text))


def thehive():
    while True:
        try:
            thehive_search('Formatted DATA:', Eq('status', 'New'))
        except Exception as e:
            logging.error("Failure attempting when attempting to escalate TheHive alerts. %s" % e)

        print("Run completed. Re-polling in 2 minutes.")
        t.sleep(120)


def ws():
    if configuration.FLASK_SETTINGS['ENABLE_WEBSERVER']:
        app.run(port=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT'], host=configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'])
    else:
        logging.warning("Flask webserver disabled. You will experience limited functionality.")


if __name__ == '__main__':
    ws = Process(target=ws)
    thehive = Process(target=thehive)
    thehive.start()
    ws.start()
    thehive.join()
    ws.join()
