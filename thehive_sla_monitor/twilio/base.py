from twilio.rest import Client

class Twilio():
    def __init__(self):
        twimlet = configuration.TWILIO_SETTINGS['TWIMLET_URL'] 
        # Initialize API classes
        twilio_client = Client(configuration.TWILIO_SETTINGS['ACCOUNT_SID'], configuration.TWILIO_SETTINGS['AUTH_TOKEN'])

    def send_sms(*args):
  for alert_id, alert_name in hive_30_dict.items():
    if alert_id in hive_30_list:
      logging.warning("Already sent SMS regarding ID: " + alert_id)
    else:
      if not is_empty(args):
        for alert_data in args:
          alert_dump = json.dumps(alert_data, indent=2)
        #  logging.info(alert_dump) # If you want to see all items in Hive response
          alert_json = json.loads(alert_dump)

          severity = (alert_json['severity']) # I want severity
          all_artifacts = (alert_json['artifacts']) # I want all artifacts
          data_artifacts = (alert_json['artifacts'][0]['data']) # I want only the data item which lies under the artifacts element

          msg_body = severity # Send only the severity
       #   msg_body = severity + " " + data_artifacts # Send severity and data_artifacts

      else:
        msg_body = 'Please attend immediately!'

      twilio_msg_body = 'TheHive SLA Alert - %s \n %s' % (alert_id, msg_body)
      message = twilio_client.messages.create(body=twilio_msg_body, from_=configuration.TWILIO_SETTINGS['TWILIO_SENDER'], to=configuration.TWILIO_SETTINGS['TWILIO_RTCP'])
      t.sleep(2)
      logging.info('SMS Sent: ' + str(message.sid))
      try:
        add_to_30m(alert_id)
      except Exception as re:
        logging.error("Error when adding to list after sending SMS: " + str(re))


    
def make_call(id):
  if id in called_list:
    logging.info("User has been called regarding ID: " + id)
  else:
    call = twilio_client.calls.create(url=twimlet, to='$insert_phone_number', from_=twilio_number)
    logging.info("Call Sent: " + str(call.sid))
    try:
      add_to_called_list(id)
    except Exception as error:
      logging.error("Error when adding to list after making call: " + str(error))