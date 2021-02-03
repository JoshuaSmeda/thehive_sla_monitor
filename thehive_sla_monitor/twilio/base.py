"""
This module is responsible for handling all Twilio integration.
"""
import json
from twilio.rest import Client

# Custom Imports
import configuration
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.alerter import seen_list, called_list, message_list
from thehive_sla_monitor.helpers import escalation_check

class Twilio():
    def __init__(self):
        if configuration.TWILIO_SETTINGS['TWILIO_ENABLED']:
            self.twimlet = configuration.TWILIO_SETTINGS['TWIMLET_URL']
            self.twilio_client = Client(configuration.TWILIO_SETTINGS['ACCOUNT_SID'], configuration.TWILIO_SETTINGS['AUTH_TOKEN'])
            self.sender = configuration.TWILIO_SETTINGS['TWILIO_SENDER']
            self.recipient = configuration.TWILIO_SETTINGS['TWILIO_RTCP']
        else:
            logging.error("Twilio is currently disabled. Please enable via configuration.py. Exiting!")
            quit()

    def send_truncated_message(self, twilio_msg_body):
        if len(self.recipient) > 1:  # More than 1 recipient specified
            for person in self.recipient:
                message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=person)
                logging.info('SMS Sent: %s' % message.sid)
        else:
            message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=''.join(self.recipient))
            logging.info('SMS Sent: %s' % message.sid)

    def send_sms(self, hive_alert, *args, **kwargs):
        escalation_check(hive_alert['id'])

        def is_empty(any_structure):
            """
            This nested method checks whether an object is empty
            """
            if any_structure:
                return False
            else:
                return True

        def char_count(msg):
            return sum(len(i) for i in msg)

        def get_total_msgs_necessary(msg):
            char_limit = 125
            get_total_number_of_msgs = total_characters / char_limit
            total_rounded = (round(get_total_number_of_msgs + 0.5))  # round up to nearest highest
            return total_rounded

        if hive_alert['id'] in message_list:
            logging.warning("TWILIO_SMS: Previously seen / ignored: %s" % hive_alert['id'])
        else:
            if not is_empty(hive_alert):
                alert_dump = json.dumps(hive_alert)
                # print(alert_dump)  # If you want to see all items in Hive response
                alert_json = json.loads(alert_dump)
                """
                Get all data from artifacts (observables and alert on it)
                """
                if len(alert_json['artifacts']) >= 1:  # Check to see if artifact has data
                    artifact_arr = []
                    for element in range(len(alert_json['artifacts'])):
                        x = alert_json['artifacts'][element]['data']
                        artifact_arr.append(x)

                    msg_body = " ".join(artifact_arr)

                    """
                    If you wish to send additional information - here is an idea:

                    severity = (alert_json['severity'])  # Collect severity
                    all_artifacts = (alert_json['artifacts'])  # Collect artifacts
                    msg_body = severity  # Send only the severity
                    msg_body = "%s %s" % severity, data_artifacts  # Send severity and data_artifacts
                    """

                else:
                    msg_body = "Please attend to immediately"

                msg_header = 'TheHive SLA Breach - %s.\nAdditional Information: %s' % (hive_alert['id'], msg_body)
                msg_body = msg_header

                total_characters = char_count(msg_body)
                logging.info("Total message character size: %s" % total_characters)
                """
                Handling Twilio SMS character limit of 160. Cut up if necessary! (Takes into account extra trial message text)
                """
                if total_characters <= 125:
                    self.send_truncated_message(msg_body)

                else:  # Start cutting message up!
                    total_msgs_necessary = (get_total_msgs_necessary(msg_body))
                    logging.info("Total number of messages: %s" % total_msgs_necessary)
                    total_msgs_necessary = (get_total_msgs_necessary(msg_body))

                    words_per_message = total_characters / get_total_msgs_necessary(msg_body)
                    words_per_message = round(words_per_message)
                    logging.info("Words per message: %s" % words_per_message)

                    out = [(msg_body[i:i + words_per_message]) for i in range(0, len(msg_body), words_per_message)]
                    count = 0
                    for msg in out:
                        count += 1
                        attach_text = " ~ ( %d / %d )" % (count, total_msgs_necessary)
                        twilio_msg_body = (msg + attach_text)
                        self.send_truncated_message(twilio_msg_body)

        message_list.append(hive_alert['id'])

    def make_call(self, alert_id):
        escalation_check(alert_id)
        if alert_id in called_list:
            logging.warning("TWILIO_CALL: Previously seen: ID: %s" % (alert_id))
        else:
            logging.info("Forwarding Twilio call")
            call = self.twilio_client.calls.create(url=self.twimlet, from_=self.sender, to=self.recipient)
            logging.info("Call Sent: %s" % call.sid)
            called_list.append(alert_id)
