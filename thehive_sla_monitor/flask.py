import configuration

#from main import promote_to_case
from thehive_sla_monitor.logger import logging
from flask import Flask, request, make_response, redirect
from thehive_sla_monitor.slack.base import Slack
from main import promote_to_case

# Instantiate Flask application
app = Flask(__name__)

@app.route("/complete/<id>", methods=['GET', 'POST'])
def complete(id):
  case_id = promote_to_case(id)
  #if case_id != None: # Handle if TheHive alert doesn't exist
  logging.info("ID: %s. Case ID: %s" % (id, case_id))

  Slack().slack_chat_update(id)

  hive_link = "http://%s:%d/index.html#!/case/%s/details" % (configuration.SYSTEM_SETTINGS['HIVE_SERVER_IP'], configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT'], case_id)
  return redirect(hive_link, code=302)

def add_to_temp_ignore(id):
  logging.info("Adding %s to ignore list" % (id))
  ignore_list.append(id)
  ignore_thread = threading.Thread(target=clean_ignore_list)
  ignore_thread.start()
  return id

@app.route("/ignore/<id>", methods=['GET', 'POST'])
def ignore(id):
  add_to_temp_ignore(id)
  ignore_id = add_to_temp_ignore(id)
  logging.info("Ignoring ID: " + ignore_id)

  #res = slack_client.chat.update(channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="TheHive SLA Monitor: Case Ignored", blocks=slack_bot_alert_notice_ignore(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
  #res = slack_client.chat.getPermalink(channel=alert_dict[id]["channel"],message_ts=alert_dict[id]["ts"])

  return ('', 204)

