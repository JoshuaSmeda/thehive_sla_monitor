"""
This module handles the Slack configuration used by the TheHive_SLA_Monitor program
"""
import configuration

from slack import WebClient
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.slack.templates import slack_bot_alert_notice_template, slack_bot_alert_notice_update, slack_bot_alert_notice_ignore
from thehive_sla_monitor.alerter import seen_list, alert_dict
from thehive_sla_monitor.helpers import escalation_check


class Slack():
    def __init__(self):
        if configuration.SLACK_SETTINGS['SLACK_ENABLED']:
            self.slack_client = WebClient(configuration.SLACK_SETTINGS['SLACK_APP_TOKEN'])
            self.channel = configuration.SLACK_SETTINGS['SLACK_CHANNEL']
        else:
            logging.error("Slack is currently disabled. Please enable via configuration.py. Exiting!")
            quit()

    def post_notice(self, alert_id, rule_name, alert_date, alert_age):
        escalation_check(alert_id)
        if alert_id in seen_list:
            logging.warning("SLACK_API: Previously seen / ignored: %s" % alert_id)
        else:
            logging.info("Executing SLACK_API Call")
            res = self.slack_client.chat_postMessage(channel=self.channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(alert_id, rule_name, alert_date, alert_age))
            alert_dict[id] = {'channel': res['channel'], 'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age}
            seen_list.append(alert_id)

    def slack_chat_update(self, id):
        self.slack_client.chat_update(channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="TheHive SLA Monitor: Case Promoted", blocks=slack_bot_alert_notice_update(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
        self.slack_client.chat_getPermalink(channel=alert_dict[id]["channel"], message_ts=alert_dict[id]["ts"])

    def slack_chat_ignore(self, id):
        self.slack_client.chat_update(channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="TheHive SLA Monitor: Case Ignored", blocks=slack_bot_alert_notice_ignore(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
        self.slack_client.chat_getPermalink(channel=alert_dict[id]["channel"], message_ts=alert_dict[id]["ts"])
