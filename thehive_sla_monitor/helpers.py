"""
This module provides helper functions that is used throughout this program.
"""
import json
import time as t
import threading

# TheHive Imports
from thehive4py.api import TheHiveApi

# Custom Imports
import configuration
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.alerter import ignore_list, called_list

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
    ignore_thread = threading.Thread(target=clean_ignore_list)
    ignore_thread.start()
    return alert_id


def add_to_called_list(alert_id):
    """
    This method adds the alert_id to the called_list
    """
    logging.info("Adding %s to called list" % alert_id)
    called_list.append(alert_id)
    return alert_id


def is_empty(any_structure):
    """
    This method checks whether an object is empty
    """
    if any_structure:
        return False
  #  else:
  #     return True


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
