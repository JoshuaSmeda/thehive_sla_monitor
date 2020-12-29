"""
This module is responsible for handling all Twilio integration.
"""
import json
import re
import itertools
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

    def send_truncated_message(self, twilio_msg_body):
        message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=''.join(self.recipient))
        logging.info('SMS Sent: %s' % message.sid)

    def send_sms(self, *args):
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
            char_limit = 100
            get_total_number_of_msgs = total_characters / char_limit
            total_rounded = (round(get_total_number_of_msgs + 0.5))  # round up to nearest highest
            return total_rounded

        for alert_id, alert_name in hive_30_dict.items():
            if alert_id in hive_30_list:
                logging.warning("Already sent SMS regarding ID: " + alert_id)
            else:
                if not is_empty(args):
                    for alert_data in args:
                        alert_dump = json.dumps(alert_data)
                        # print(alert_dump)  # If you want to see all items in Hive response
                        alert_json = json.loads(alert_dump)
                        if len(alert_json['artifacts']) >= 1:  # Check to see if artifact has data
                            print("greater than 1")
                            artifact_arr = []
                            for element in range(len(alert_json['artifacts'])):
                                x = alert_json['artifacts'][element]['data']
                                artifact_arr.append(x)

                            print(artifact_arr)

#                            data_artifacts = (alert_json['artifacts'][0]['data'])
                        """
                        If you wish to send additional information:

                        severity = (alert_json['severity'])  # Collect severity
                        all_artifacts = (alert_json['artifacts'])  # Collect artifacts
                        msg_body = severity  # Send only the severity
                        msg_body = "%s %s" % severity, data_artifacts  # Send severity and data_artifacts
                        """
                        # msg_body = 'Please attend immediately!'
                        msg_body = "When in the course of human Events, it becomes necessary for one People to dissolve the Political Bands which have connected them with another, and to assume among the Powers of the Earth, the separate and equal Station to which the Laws of Nature and of Nature?s God entitle them, a decent Respect to the Opinions of Mankind requires that they should declare the causes which impel them to the Separation"

                        total_characters = char_count(msg_body)
                        print("Total message size: " + str(total_characters))
                        if total_characters <= 100:
                            # send the message as is - there is no need to truncate
                            print("less than 150")

                        else:  # safety limit - start cutting myself up
                            print("we need to split up into x amount of messages")
                            total_msgs_necessary = (get_total_msgs_necessary(msg_body))

                            words_per_message = total_characters / get_total_msgs_necessary(msg_body)
                            words_per_message = round(words_per_message)
                            print("WPM: " + str(words_per_message))

                            out = [(msg_body[i:i + words_per_message]) for i in range(0, len(msg_body), words_per_message)]
                            count = 0
                            for msg in out:
                                count += 1
                                attach_text = " ~ ( %d / %d )" % (count, total_msgs_necessary)
                                twilio_msg_body = (msg + attach_text)
                                self.send_truncated_message(twilio_msg_body)
              
                # else:
                #    msg_body = 'Please attend immediately!'

                # twilio_msg_body1 = 'TheHive SLA Breach Detected. Alert_ID: \nAdditional Information: '  # around 64 words, round up to 80

                twilio_msg_body = 'TheHive SLA Breach Detected. Alert_ID: %s.\nAdditional Information: %s' % (alert_id, msg_body)

                if len(self.recipient) > 1:  # More than 1 recipient specified
                    for person in self.recipient:
                        message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=person)
                        logging.info('SMS Sent: %s' % message.sid)
                else:
                    pass
                    # message = self.twilio_client.messages.create(body=twilio_msg_body, from_=self.sender, to=''.join(self.recipient))
                    # logging.info('SMS Sent: %s' % message.sid)

    def make_call(self, alert_id):
        if alert_id in hive_45_list:
            logging.info("Already called regarding ID: " + alert_id)
        else:
            call = self.twilio_client.calls.create(url=self.twimlet, from_=self.sender, to=self.recipient)
            logging.info("Call Sent: %s" % call.sid)
