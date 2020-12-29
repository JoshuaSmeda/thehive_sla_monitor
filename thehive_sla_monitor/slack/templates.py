import configuration


def slack_bot_alert_notice_template(alert_id, rule_name, alert_date, alert_age):
    data = \
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "A new SLA breach has been raised:\n*<" + configuration.SYSTEM_SETTINGS['HIVE_FQDN'] + ":" + str(configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']) + "/index.html|The Hive>*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alert ID:*\n" + alert_id + "\n*Triggered Rule:*\n" + rule_name + "\n*Alert Created:*\n" + alert_date + "\n*Alert Age:*\n" + alert_age
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://images.g2crowd.com/uploads/product/image/large_detail/large_detail_a68ccc480d8ab103641960b1c5fc9fbb/thehive.png",
                    "alt_text": "The Hive Project"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "url": "http://" + configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'] + ":" + str(configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT']) + "/complete/" + alert_id,
                        "text": {
                            "type": "plain_text",
                            "text": "Promote To Case"
                        },
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "url": "http://" + configuration.FLASK_SETTINGS['FLASK_WEBSERVER_IP'] + ":" + str(configuration.FLASK_SETTINGS['FLASK_WEBSERVER_PORT']) + "/ignore/" + alert_id,
                        "text": {
                            "type": "plain_text",
                            "text": "Ignore Case"
                        },
                        "style": "danger",
                    }
                ]
            }
        ]
    return data


def slack_bot_alert_notice_update(alert_id, rule_name, alert_date, alert_age):
    data = \
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "A new SLA breach has been raised:\n*<" + configuration.SYSTEM_SETTINGS['HIVE_FQDN'] + ":" + str(configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']) + "/index.html|The Hive>*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alert ID:*\n" + alert_id + "\n*Triggered Rule:*\n" + rule_name + "\n*Alert Created:*\n" + alert_date + "\n*Alert Age:*\n" + alert_age
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://images.g2crowd.com/uploads/product/image/large_detail/large_detail_a68ccc480d8ab103641960b1c5fc9fbb/thehive.png",
                    "alt_text": "The Hive Project"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":heavy_check_mark: *Successfully Imported Case!*"
                }
            }
        ]
    return data


def slack_bot_alert_notice_ignore(alert_id, rule_name, alert_date, alert_age):
    data = \
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "A new SLA breach has been raised:\n*<" + configuration.SYSTEM_SETTINGS['HIVE_FQDN'] + ":" + str(configuration.SYSTEM_SETTINGS['HIVE_SERVER_PORT']) + "/index.html|The Hive>*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alert ID:*\n" + alert_id + "\n*Triggered Rule:*\n" + rule_name + "\n*Alert Created:*\n" + alert_date + "\n*Alert Age:*\n" + alert_age
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://images.g2crowd.com/uploads/product/image/large_detail/large_detail_a68ccc480d8ab103641960b1c5fc9fbb/thehive.png",
                    "alt_text": "The Hive Project"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":x: *Case Temporarily Ignored!*"
                }
            }
        ]
    return data
