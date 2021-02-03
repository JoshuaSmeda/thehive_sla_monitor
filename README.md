[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/JoshuaSmeda/TheHive_SLA_Monitor/issues)
![build_python](https://github.com/JoshuaSmeda/thehive_sla_monitor/workflows/build_python/badge.svg)

# TheHive_SLA_Monitor
This applications runs as a Linux service, queries TheHive (SIRP) alerts based on a set severity status while cross checking set SLA limits and then SMS's or calls specified people if there is a breach. This is achieved with the following technologies:

```
Python3
Flask
Twilio
Slack
TheHive (SIRP)
```

## Overview:

This application connects to your slack workspace using the Slack API. The application periodically polls the TheHive (every 2 minutes) https://thehive-project.org/ using a pre-defined API key. It grabs all pending alerts with a severity status of 3 (high) and performs SLA checks on the alerts. The following SLA's are outlined below:

30 minutes - SMS person scheduled "on-call" <br>
45 minutes - Call person scheduled "on-call" and echo a generic, pre-defined, message via Twilio using a Twimlet<br>
60 minutes - Escalate to seniors members, through phone call via Twilio <br>

Once a alert fires, it won't be re-alert on unless it hits a new SLA tier (e.g. Moves from 30 minutes to 45 minutes).

Each alert will create a slack notice that allows you to promote to case or ignore the alert for 30 minutes from within Slack instead of manually acknowledging the alert via the TheHive web interface. When promoting a case, Slack will link you to the imported case, when ignoring, the alert won't re-alert at 45 / 60 minutes for 30 minutes.

A log record is generated each transactional event which allows you to track and audit events.


## Configuration parameters:

The `configuration.py` is utilized as a central location to modify functionality and parameters related to the program. Such as, changing the severity level you wish to search TheHive for, or adjusting the SLA timers you wish to poll at. 

The following explains the parameters accepted:

```

SLA_SETTINGS = {
     # Int: seconds to classify the age of a low severity SLA breach in the form of seconds
     # Note: Do not adjust the key name as it's used in conjunction with a switch case function within the program.
     # This nested dictionary allows you to configure whether you want to enable alerting for each of the 3 tiers provided by TheHive. Adjust the TIMER accordingly based on your SLA requirements
     # and the NOTIFICATION_METHOD. You can include a single method, or even multiple if your use-case requires so.
     # The HIGH_RISK object is necessary for any high_word_risk triggers - do not remove!

     'THEHIVE_LEVEL1': {'ENABLED': True,
                       'LOW_SEVERITY': {'TIMER': 1800, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_SMS']},
                       'MEDIUM_SEVERITY': {'TIMER': 2700, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_ESC']},
                       'HIGH_SEVERITY': {'TIMER': 3600, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_CALL']},
                       'HIGH_RISK': {'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_CALL']}},

     'THEHIVE_LEVEL2': {'ENABLED': True,
                       'LOW_SEVERITY': {'TIMER': 1800, 'NOTIFICATION_METHOD': ['TWILIO_SMS']},
                       'MEDIUM_SEVERITY': {'TIMER': 2700, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_SMS']},
                       'HIGH_SEVERITY': {'TIMER': 3600, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_CALL']},
                       'HIGH_RISK': {'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_CALL']}},

     'THEHIVE_LEVEL3': {'ENABLED': True,
                       'LOW_SEVERITY': {'TIMER': 1800, 'NOTIFICATION_METHOD': ['SLACK_API']},
                       'MEDIUM_SEVERITY': {'TIMER': 2700, 'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_SMS']},
                       'HIGH_SEVERITY': {'TIMER': 3600, 'NOTIFICATION_METHOD': ['TWILIO_CALL']},
                       'HIGH_RISK': {'NOTIFICATION_METHOD': ['SLACK_API', 'TWILIO_CALL']}}
}

SYSTEM_SETTINGS = {
    'HIGH_RISK_WORDS': ['CRITICAL', 'URGENT', 'FAILURE']  # List: Add custom words here that you want to be critically alerted on. These words must be included (non-case sensitive) in the Hive title or in one of the artifacts. This will immediately escalate to HIGH_SEVERITY SLA.
    'HIGH_RISK_WORDS_SEVERITY_LEVEL': 2, # Integer: Adjust the specific severity level you want high_risk_words to specifically run on. For example, if you only want high_risk_words triggers on TheHive severity 3 alerts.
    'HIVE_SERVER_IP': '192.168.1.15',  # String: The server IP or functioning DNS name of the TheHive instance you would like to query.
    'HIVE_SERVER_PORT': 9000,  # Int: The TheHive port that's exposed to the instance this program will be running from.
    'HIVE_FQDN': 'http://192.168.1.15',  # String: The FQDN of the TheHive instance.
    'HIVE_API_KEY': 'iIMm25V63IjkoLN0MlsJJTcdrPYYhyBi',  # String: The TheHive API key generated for the API user you created.
    'LOG_FILE_LOCATION': 'debug.log'  # String: The file location where you would like to store your logs. You can specify a file path as well.
}

FLASK_SETTINGS = {
    'ENABLE_WEBSERVER': True,  # Boolean: Toggle to enable Flask to enrich the Slack integration. Set to False to disable.
    'FLASK_WEBSERVER_IP': '192.168.1.200',  # String: The IP of the instance you running this program on (will act as a webserver so needs to be reachable).
    'FLASK_WEBSERVER_PORT': 3000  # Int: The webserver port you wish to expose Flask on.
}

TWILIO_SETTINGS = {
    'TWILIO_ENABLED': True,  # Boolean: Toggle to enable Twilio functionality. Set to False to disable.
    'TWILIO_SENDER': '+123456789',  # String: The Twilio number you wish to send from. Obtain from your Twilio console.
    'TWILIO_RTCP': ['+123456789', '+123456789'],  # List: A list of numbers you wish to send notifications via Twilio to.
    'ACCOUNT_SID': '',  # String: Your Twilio account SID. Obtain from Twilio console.
    'AUTH_TOKEN': '',  # String: Your Twilio auth token. Obtain from Twilio console.
    'TWIMLET_URL': 'http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%3EHi+there.%3C%2FSay%3E%3C%2FResponse%3E'  # String: The FQDN to your custom Twimlet if you have one hosted. Create one here: https://www.twilio.com/labs/twimlets/echo.
}

SLACK_SETTINGS = {
    'SLACK_ENABLED': True,  # Boolean: Toggle to enable Slack functionality. Set to False to disable.
    'SLACK_APP_TOKEN': '',  # String: Your Slack application token. Obtain from your Slack console.
    'SLACK_CHANNEL': '',  # String: Your Slack application channel ID. Obtain from your Slack instance.
    'SLACK_WEBHOOK_URL': ''  String: Your Slack application webhook URL you generated. Obtain frmo your Slack instance.
}
```


## Adjust what gets alerted on:

If you wish to adjust / add / remove what happens when a alert hits a specified SLA tier and the alert method that gets triggered (i.e, send via Twilio / send via Slack). You can adjust the definitions under the `classmethods` within `main.py`

Existing configuration for reference to compare with below:

```
class EscalationSelector:
    """
    Dynamically escalate Hive alerts based on configured severity
    """
    @classmethod
    def escalate(cls, severity, *args, **kwargs):
        """
        This classmethod executes the approriate classmethod based on the providers severity attribute.
        """
        getattr(cls, f'{severity}')(*args, **kwargs)

    @classmethod
    def low_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and sends an SMS to the person currently "on-call".
        """
        logging.warning('LowSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_30_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)
        Twilio().send_sms(*args)

    @classmethod
    def medium_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and makes a call to the person currently "on-call".
        """
        logging.warning('MediumSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_45_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)
        Twilio().make_call(alert_id)

    @classmethod
    def high_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
        """
        This classmethod alerts via Slack and makes an escalated call once this tier is reached.
        """
        logging.warning('HighSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
        Alerter().add_to_60_dict(alert_id, rule_name)
        Slack().post_notice(alert_id, rule_name, alert_date, alert_age)

```

For example:

Removing `Slack` posting for `high_severity` alerts:

```
@classmethod
def high_severity(cls, alert_id, rule_name, alert_date, alert_age, *args, **kwargs):
  """
  This classmethod alerts via Slack and makes an escalated call once this tier is reached.
  """
  logging.warning('HighSeverity: Alert ID: %s. Rule Name: %s. Alert Date: %s. Alert Age: %s' % (alert_id, rule_name, alert_date, alert_age))
  Alerter().add_to_60_dict(alert_id, rule_name)
  # Removed the Slack function reference!
```

## How to install:

To do:

Create a slack application to receive messages to your workspace - follow this guide: https://github.com/slackapi/python-slack-sdk/blob/main/tutorial/01-creating-the-slack-app.md <br>
Create a "echo" twimlet to playback a custom voice message when called by Twilio: https://www.twilio.com/labs/twimlets/echo <br>
Create a twilio account to receive calls / sms's

1. Install Python Virtual Environment ```python3 -m venv env```
2. Activate Virtual Environment ``` . env/bin/activate```
3. Install dependencies ```pip install -r requirements.txt```
4. Add in custom variables in ```configuration.py``` which is injected into the main application at runtime.
5. Run using ```python main.py``` - if you wish to run as a service, see below:

It's recommended to setup a reverse proxy to forward requests to your Python Flask server running (defined within ```configuration.py```). Here's a mini example using Nginx. Note, this is not configured for production use. Replace ```x.x.x.x``` with the IP address you plan on having your application listen on.

```
server {
  listen 80;

  location /web_api/ {
    proxy_pass http://x.x.x.x:3000/;
  }
}

```

Alternatively you can use ```ngrok.com``` to tunnel if you do not wish to use a webserver. This is discouraged due to the potential security risks associated with this.

## Create sysinitv service on Linux (Debian):

Place in ```/etc/systemd/system/thehive_sla_monitor.service```

```
[Unit]
Description=TheHive SLA Monitor

[Service]
Type=simple
ExecStart=/path/to/dir/env/bin/python /path/to/dir/main.py
WorkingDirectory=/path/to/dir/

[Install]
WantedBy=sysinit.target
```

Reload the daemon:

```systemctl daemon-reload```

Run / Start the bot with ```service thehive_sla_monitor start```.
