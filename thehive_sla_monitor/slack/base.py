import configuration

from slack import WebClient
from thehive_sla_monitor.logger import logging
from thehive_sla_monitor.slack.templates import slack_bot_alert_notice_template, slack_bot_alert_notice_update, slack_bot_alert_notice_ignore

from thehive_sla_monitor.alerter import *

class Slack():
    def __init__(self):
        slack_webhook_url = configuration.SLACK_SETTINGS['SLACK_WEBHOOK_URL']
        self.slack_client = WebClient(configuration.SLACK_SETTINGS['SLACK_APP_TOKEN'])
        self.channel = configuration.SLACK_SETTINGS['SLACK_CHANNEL']

    def post_notice(self, id, rule_name, alert_date, alert_age):
        for k,v in hive_30_dict.items():
            if k in hive_30_list or k in ignore_list:
                logging.warning("Already notified regarding ID / Previously ignored: " + k)
            else:
                res = self.slack_client.chat_postMessage(channel=self.channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
                
        for k,v in hive_45_dict.items():
            if k in hive_45_list or k in ignore_list:
                logging.warning("Already notified regarding ID / Previously ignored: " + k)
            else:
                res = self.slack_client.chat_postMessage(channel=self.channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
        
        for k,v in hive_60_dict.items():
            if k in hive_60_list or k in ignore_list:
                logging.warning("Already notified regarding ID or previously ignored: %s" % k)
            else:
                res = self.slack_client.chat_postMessage(channel=self.channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }

    def slack_chat_update(self, id):
        print(alert_dict)
        print(id)
        print(alert_dict[id]["ts"])
       # self.slack_client.chat.update(channel=alert_dict[id]['channel'], ts=alert_dict[id]["ts"], text="TheHive SLA Monitor: Case Promoted", blocks=slack_bot_alert_notice_update(id, alert_dict[id]['rule_name'], alert_dict[id]['alert_date'], alert_dict[id]['alert_age']))
       # self.slack_client.chat.getPermalink(channel=alert_dict[id]["channel"], message_ts=alert_dict[id]["ts"])