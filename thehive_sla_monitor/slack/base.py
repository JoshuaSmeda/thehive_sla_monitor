import configuration

from slack import WebClient
from thehive_sla_monitor.logger import logging

class Slack():
    def __init__(self):
        slack_webhook_url = configuration.SLACK_SETTINGS['SLACK_WEBHOOK_URL']
        slack_client = WebClient(configuration.SLACK_SETTINGS['SLACK_APP_TOKEN'])
        channel = configuration.SLACK_SETTINGS['SLACK_CHANNEL']
        print("slack")

    def slack_bot_notice_alert(self, channel, id, rule_name, alert_date, alert_age):
        for k,v in hive_30_dict.items():
            if k in hive_30_list or k in ignore_list:
                logging.warning("Already notified regarding ID / Previously ignored: " + k)
            else:
                res = slack_client.chat_postMessage(channel=channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
        for k,v in hive_45_dict.items():
            if k in hive_45_list or k in ignore_list:
                logging.warning("Already notified regarding ID / Previously ignored: " + k)
            else:
                res = slack_client.chat_postMessage(channel=channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
        for k,v in hive_60_dict.items():
            if k in hive_60_list or k in ignore_list:
                logging.warning("Already notified regarding ID / Previously ignored: " + k)
            else:
                res = slack_client.chat_postMessage(channel=channel, text="TheHive SLA Monitor: SLA Breach", blocks=slack_bot_alert_notice_template(id, rule_name, alert_date, alert_age))
                alert_dict[id] = {'channel': res['channel'],'ts': res['message']['ts'], 'rule_name': rule_name, 'alert_date': alert_date, 'alert_age': alert_age }
