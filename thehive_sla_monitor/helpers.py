"""
This module provides helper functions that is used throughout this program.
"""
import json
import threading
import time as t
import itertools
from datetime import datetime

# Custom Imports
import configuration
from thehive4py.api import TheHiveApi
from thehive_sla_monitor.alerter import called_list, ignore_list, low_sev_list, med_sev_list, high_sev_list, seen_list
from thehive_sla_monitor.logger import logging

# Defining variables

HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']
HIVE_API_KEY = configuration.SYSTEM_SETTINGS['HIVE_API_KEY']
HIVE_API = TheHiveApi("http://%s:%s" % (HIVE_SERVER_IP, HIVE_SERVER_PORT), HIVE_API_KEY)


def clean_ignore_list(alert_id):
    """
    This method clears the ignore_list after 30 minutes.
    """
    t.sleep(3600)
    logging.info("Removing %s from ignore list" % alert_id)
    ignore_list.remove(alert_id)


def add_to_temp_ignore(alert_id):
    """
    This method adds the alert_id to the ignore_list as a thread to avoid being re-alerted on.
    """
    logging.info("Adding %s to ignore list" % alert_id)
    ignore_list.append(alert_id)
    ignore_thread = threading.Thread(target=clean_ignore_list, args=(alert_id,))
    ignore_thread.start()
    return alert_id


def add_to_called_list(alert_id):
    """
    This method adds the alert_id to the called_list
    """
    logging.info("Adding %s to called list" % alert_id)
    called_list.append(alert_id)
    return alert_id


def promote_to_case(case_id):
    """
    This method promotes a provided alert to an case via the Hive
    """
    logging.info("Promoting Alert %s" % case_id)
    response = HIVE_API.promote_alert_to_case(case_id)
    if response.status_code == 201:
        data = json.dumps(response.json())
        jdata = json.loads(data)
        case_id = (jdata['id'])
        return case_id
    else:
        logging.error('TheHive: {}/{}'.format(response.status_code, response.text))


def high_risk_escalate(alert):
    """
    This method accepts an alert, performs checks against the data and if there is a title or artifact that has a high risk word in it,
    return True
    """
    high_risk_detected = False
    if len(alert['artifacts']) >= 1:  # Check to see if artifact has data
        artifact_arr = []
        for element in range(len(alert['artifacts'])):
            x = alert['artifacts'][element]['data']
            artifact_arr.append(x)

    for word in configuration.SLA_SETTINGS['HIGH_RISK_WORDS']:
        if any(word.lower() in s.lower() for s in artifact_arr):
            high_risk_detected = True
        elif word.lower() in alert['title'].lower():
            high_risk_detected = True
    if high_risk_detected:
        return True
    else:
        return False

def get_alert_timer(hive_alert):
    """
    This function takes in a hive_alert and performs a calculation to determine the alerts age based on the current datetime. We used this to check against SLA limits.
    """
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    timestamp = int(hive_alert['createdAt'])
    timestamp /= 1000
    alert_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
    diff = (current_date - alert_date)
    return alert_date, diff


def get_active_sla(dct):
    active_dicts = []
    for obj in dct:
        try:
            if dct[obj]['ENABLED']:
                active_dicts.append(obj)
        except TypeError:
            continue
    return active_dicts


def get_sla_data(dct, obj):
    data = {}
    keys = []
    for element in dct[obj]:
        if 'ENABLED' in element:
            continue  # Skip enabled obj
        keys.append(element)
    for k in keys:
        data[k] = {'TIMER': dct[obj][k]['TIMER'], 'NOTIFICATION_METHOD': dct[obj][k]['NOTIFICATION_METHOD']}

    tuple_obj = ()
    for x in data:
        tuple_obj += (data[x],)
    return tuple_obj

def escalation_check(alert_id):
    if alert_id in low_sev_list and alert_id in med_sev_list:
        print("Removing alert from seen_list as it's moved up a tier")
        seen_list.remove(alert_id)
        low_sev_list.remove(alert_id)

    elif alert_id in med_sev_list and alert_id in high_sev_list:
        print("Removing alert from seen_list as it's moved a tier (2nd)")
        seen_list.remove(alert_id)
        med_sev_list.remove(alert_id)
    else:
        print('Nothing to change!!')


#    print(set(low_sev_list).intersection(med_sev_list, high_sev_list))

    #for aval, bval, cval in itertools.product(low_sev_list, med_sev_list, high_sev_list):
    #    if aval == bval and bval == cval:
    #        print(aval)

    #print([i for i, j in zip(low_sev_list, med_sev_list) if i == j])

    #[x for x in a if x in b]