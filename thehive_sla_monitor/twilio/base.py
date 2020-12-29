"""
This module is responsible for handling all Twilio integration.
"""
import json
from twilio.rest import Client

# Custom Imports
import configuration
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.alerter import hive_30_dict, hive_30_list, hive_45_list


class Twilio():
    def __init__(self):
        self.twimlet = configuration.TWILIO_SETTINGS['TWIMLET_URL']
        self.twilio_client = Client(configuration.TWILIO_SETTINGS['ACCOUNT_SID'], configuration.TWILIO_SETTINGS['AUTH_TOKEN'])
        self.sender = configuration.TWILIO_SETTINGS['TWILIO_SENDER']
        self.recipient = configuration.TWILIO_SETTINGS['TWILIO_RTCP']

    def send_sms(self, *args):
        def is_empty(any_structure):
            """
            This nested method checks whether an object is empty
            """
            if any_structure:
                return False
            else:
                return True

        for alert_id, alert_name in hive_30_dict.items():
            if alert_id in hive_30_list:
                logging.warning("Already sent SMS regarding ID: " + alert_id)
            else:
                if not is_empty(args):
                    for alert_data in args:
                        alert_dump = json.dumps(alert_data)
                        # logging.info(alert_dump) # If you want to see all items in Hive response
                        alert_json = json.loads(alert_dump)
                        if len(alert_json['artifacts']) != 0:  # Check to see if artifact has data
                            data_artifacts = (alert_json['artifacts'][0]['data'])
                        """
                        If you wish to send additional information:

                        severity = (alert_json['severity'])  # Collect severity
                        all_artifacts = (alert_json['artifacts'])  # Collect artifacts
                        msg_body = severity  # Send only the severity
                        msg_body = "%s %s" % severity, data_artifacts  # Send severity and data_artifacts
                        """
                        msg_body = 'Please attend immediately!'
                else:
                    msg_body = 'Please attend immediately!'

                twilio_msg_body = 'TheHive SLA Breach Detected. Alert_ID: %s.\nAdditional Information: %s' % (alert_id, msg_body)
                
                if len(self.recipient) > 1:  # More than 1 recipient specified
                    for person in self.recipient:
                        message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=person)
                        logging.info('SMS Sent: %s' % message.sid)
                else:
                    message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=''.join(self.recipient))
                    logging.info('SMS Sent: %s' % message.sid)

    def make_call(self, alert_id):
        if alert_id in hive_45_list:
            logging.info("Already called regarding ID: " + alert_id)
        else:
            call = self.twilio_client.calls.create(url=self.twimlet, from_=self.sender, to=self.recipient)
            logging.info("Call Sent: %s" % call.sid)
