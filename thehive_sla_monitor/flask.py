"""
This module defines the configuration for the Flask webserver.
Used in conjuction with the Slack intregration.
"""

import configuration

# Custom Imports
from flask import Flask, redirect
from waitress import serve
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.slack.base import Slack
from thehive_sla_monitor.helpers import add_to_temp_ignore, promote_to_case

# Instantiate Flask application
app = Flask(__name__)
HIVE_SERVER_IP = configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP']
HIVE_SERVER_PORT = configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']


@app.route("/complete/<alert_id>", methods=['GET', 'POST'])
def complete(alert_id):
    """
    This method executes a promotion via the Hive for the selected alert_id
    The original Slack message is also updated
    The user is redirected to the approriate case via the Hive
    """
    case_id = promote_to_case(alert_id)
    # if case_id != None: # Handle if TheHive alert doesn't exist
    logging.info("ID: %s. Case ID: %s" % (alert_id, case_id))
    Slack().slack_chat_update(alert_id)
    hive_link = "http://%s:%d/index.html#!/case/%s/details" % (HIVE_SERVER_IP, HIVE_SERVER_PORT, case_id)
    return redirect(hive_link, code=302)


@app.route("/ignore/<alert_id>", methods=['GET', 'POST'])
def ignore(alert_id):
    """
    This method adds the alert_id to the ignore list and updates the original Slack message
    """
    add_to_temp_ignore(alert_id)
    ignore_id = add_to_temp_ignore(alert_id)
    logging.info("Ignoring ID: %s" % ignore_id)
    Slack().slack_chat_ignore(alert_id)
    return ('', 204)
