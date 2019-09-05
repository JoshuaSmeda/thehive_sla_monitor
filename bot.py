from __future__ import print_function
from __future__ import unicode_literals

import time as t
import sys
import json, ast
import threading
import os
import re
from multiprocessing import Process, Queue, Manager
from flask import Flask, request, make_response, redirect
from datetime import datetime, time
from slackclient import SlackClient
from twilio.rest import Client
from thehive4py.api import TheHiveApi
from thehive4py.query import *
from soc_bot.templates import slack_bot_pick_user_template, slack_bot_alert_notice_template, slack_bot_alert_notice_update, slack_bot_alert_notice_ignore
from soc_bot.logger import collect_logs, log_current_time

# Instantiate Hive variables
sla_30 = 1800
sla_45 = 2700
sla_60 = 3600
hive_30_list = []
hive_30_dict = {}
hive_45_list = []
hive_45_dict = {}
hive_60_list = []
hive_60_dict = {}
ignore_list = []
called_list = []
hive_api_key = '$insert_hive_api_key'

# Instantiate Slack & Twilio variables
twilio_number = "$insert_twilio_number"
twilio_auth_token = '$insert_twilio_auth_token'
twilio_account_sid = '$insert_twilio_account_sid'
slack_webhook_url = '$insert_slack_channel_webhook'
twimlet = "$insert_created_twimlet"

# Initialize API classes
slack_client = SlackClient('xoxb-131509810032-507548775220-sMTWT3na0YlRq1VMBEYXblKo')
twilio_client = Client(twilio_account_sid, twilio_auth_token)
api = TheHiveApi('$insert_hive_ip & port e.g http://169.254.1.1:9000', hive_api_key)
channel = 'CET23BHJS'

# Instatiate Flask classes
app = Flask(__name__)
manager = Manager()
alert_dict = manager.dict()

def create_hive30_dict(id, rule_name, alert_date, alert_age):
  print("Updating 30M SLA dictionary")
  hive_30_dict.update({ id : rule_name, })
  slack_bot_notice_alert(channel, id, rule_name, alert_date, alert_age)
  send_sms()

def create_hive45_dict(id, rule_name, alert_date, alert_age):
  print("Updating 45M SLA dictionary")
  hive_45_dict.update({ id : rule_name, })
  slack_bot_notice_alert(channel, id, rule_name, alert_date, alert_age)
  make_call(id)

def create_hive60_dict(id, rule_name, alert_date, alert_age):
  hive_60_dict.update({ id : rule_name, })
  slack_bot_notice_alert(channel, id, rule_name, alert_date, alert_age)
  collect_logs(str(log_current_time()) + ' Alert ID: ' + id + ' Rule Name: ' + rule_name + ' Alert Date: ' + alert_date + ' Alert Age: ' + alert_age)
  # escalate to a senior

def add_to_30m(id):
  if id in hive_30_list:
    print('Already added - 30 minute SLA list: ' + id)
  else:
    print('Appending - 30 minute SLA list: ' + id)
    hive_30_list.append(id)

def add_to_45m(id):
  if id in hive_45_list:
    print('Already added - 45 minute SLA list: ' + id)
  else:
    print('Appending - 45 minute SLA list: ' + id)
    hive_45_list.append(id)

def add_to_60m(id):
  if id in hive_60_list:
    print('Already added - 60 minute SLA list: ' + id)
  else:
    print('Appending - 60 minute SLA list: ' + id)
    hive_60_list.append(id)

def clean_ignore_list(id):
  time.sleep(3600)
  print("Removing " + id + " from ignore list")
  ignore_list.remove(id)

def add_to_temp_ignore(id):
  print("Adding " + id + " to ignore list")
  ignore_list.append(id)
  ignore_thread = threading.Thread(target=clean_ignore_list)
  ignore_thread.start()
  return id

def add_to_called_list(id):
  print("Adding " + id + " to called list")
  called_list.append(id)
  return id

def search(title, query):
  current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
  response = api.find_alerts(query=query)

  if response.status_code == 200:
    data = json.dumps(response.json())
    jdata = json.loads(data)
    for d in jdata:
      if d['severity'] == 3:
        ts = int(d['createdAt'])
        ts /= 1000
        alert_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(d['id'] + " " + d['title'] + " " + str(alert_date))
        alert_date = datetime.strptime(alert_date, '%Y-%m-%d %H:%M:%S')
        diff = (current_date - alert_date)
        if sla_30 < diff.total_seconds() and sla_45 > diff.total_seconds():
          print("30/M SLA: " + str(diff) + " " + d['id'])
          create_hive30_dict(d['id'], d['title'], str(alert_date), str(diff))
          add_to_30m(d['id'])
        elif sla_45 < diff.total_seconds() and sla_60 > diff.total_seconds():
          print("45/M SLA: " + str(diff) + " " + d['id'])
          create_hive45_dict(d['id'], d['title'], str(alert_date), str(diff))
          add_to_45m(d['id'])
        elif sla_60 < diff.total_seconds():
          print("60/M SLA: " + str(diff) + " " + d['id'])
          create_hive60_dict(d['id'], d['title'], str(alert_date), str(diff))
          add_to_60m(d['id'])

    print('')

  else:
    print('ko: {}/{}'.format(response.status_code, response.text))

def send_sms():
  for k,v in hive_30_dict.iteritems():
    if k in hive_30_list:
      print("Already sent SMS regarding ID: " + k)
    else:
      body = 'Hive Alert SLA Notice - ' + "\n" + v
      send_from = twilio_number
      send_to = '$_insert_number'
      message = twilio_client.messages.create(body=body, from_=send_from, to=send_to)
      print("SMS Sent: " + str(message.sid))
      try:
        add_to_30m(k)
      except Exception as error:
        print("Error when adding to list after sending SMS: " + str(error))

def make_call(id):
  if id in called_list:
    print("User has been called regarding ID: " + id)
  else:
    call = twilio_client.calls.create(url=twimlet, to='$insert_phone_number', from_=twilio_number)
    print("Call Sent: " + str(call.sid))
    try:
      add_to_called_list(id)
    except Exception as error:
      print("Error when adding to list after making call: " + str(error))

# Print call list for record purposes?
#    calls = twilio_client.calls.list(limit=1)
#    for record in calls:
#      print(str(record.start_time) + " " + str(record.to) + " " + str(record.status))
#   https://www.twilio.com/docs/voice/api/call#parameters

def slack_bot_notice_alert(channel, id, rule_name, alert_date, alert_age):
  for k,v in hive_30_dict.iteritems():
    if k in hive_30_list or k in ignore_list:
      print("Already notified regarding ID / Previously ignored: " + k)
    else:
      res = slack_client.api_call("chat.postMessage", channel=channel, text="SOC Bot: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
      alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
  for k,v in hive_45_dict.iteritems():
    if k in hive_45_list or k in ignore_list:
      print("Already notified regarding ID / Previously ignored: " + k)
    else:
      res = slack_client.api_call("chat.postMessage", channel=channel, text="SOC Bot: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
      alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
  for k,v in hive_60_dict.iteritems():
    if k in hive_60_list or k in ignore_list:
      print("Already notified regarding ID / Previously ignored: " + k)
    else:
      res = slack_client.api_call("chat.postMessage", channel=channel, text="SOC Bot: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
      alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }

def promote_to_case(case_id):
  print("Promoting Alert " + case_id)
  response = api.promote_alert_to_case(case_id)
  if response.status_code == 201:
    data = json.dumps(response.json())
    jdata = json.loads(data)
    case_id = (jdata['id'])
    return case_id
  else:
    print('ko: {}/{}'.format(response.status_code, response.text))

@app.route("/complete/<id>", methods=['GET', 'POST'])
def complete(id):
  case_id = promote_to_case(id)
  print("ID: " + id + " Case ID: " + case_id)

  res = slack_client.api_call("chat.update", channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="SOC Bot: Case Promoted", blocks=slack_bot_alert_notice_update(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
  res = slack_client.api_call("chat.getPermalink",channel=alert_dict[id]["channel"],message_ts=alert_dict[id]["ts"])

  hive_link = "https://$insert_server_ip/hive/index.html#/case/{}/details".format(case_id)
  return redirect(hive_link, code=302)

@app.route("/ignore/<id>", methods=['GET', 'POST'])
def ignore(id):
  print(id)
  add_to_temp_ignore(id)
  ignore_id = add_to_temp_ignore(id)
  print("Ignoring ID: " + ignore_id)

  res = slack_client.api_call("chat.update", channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="SOC Bot: Case Ignored", blocks=slack_bot_alert_notice_ignore(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
  res = slack_client.api_call("chat.getPermalink",channel=alert_dict[id]["channel"],message_ts=alert_dict[id]["ts"])

  return ('', 204)

def bot_start():
  while True:
    search('Formatted DATA:', Eq('status', 'New'))
    t.sleep(120)

def webserver_start():
    app.run(port=3000, host='$insert_server_ip_here_where_you_wish_to_bind_webserver_on')
    return

if __name__ == '__main__':
  webserver_start = Process(target=webserver_start)
  bot_start = Process(target=bot_start)
  bot_start.start()
  webserver_start.start()
  bot_start.join()
  webserver_start.join()
