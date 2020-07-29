[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/JoshuaSmeda/TheHive_SLA_Monitor/issues)

# TheHive_SLA_Monitor
This applications runs as a Linux service, queries TheHive alerts based on a set severity status while cross checking set SLA limits and then SMS's or calls specified people if there is a breach. This is achieved with the following technologies:

Python3 <br>
Flask <br>
Twilio <br>
Slack <br>
TheHive (SIRP) <br>

## Overview:

This application connects to your slack workspace using the Slack API. The application periodically polls the TheHive (every 2 minutes) https://thehive-project.org/ using a pre-defined API key. It grabs all pending alerts with a severity status of 3 (high) and performs SLA checks on the alerts. The following SLA's are outlined below:

30 minutes - SMS person on shift <br>
45 minutes - Call person on shift and playback a message via Twilio<br>
60 minutes - Escalate to seniors, through call <br>

Once a alert fires, it won't be re-alert on unless it hits a new SLA tier (e.g. Moves from 30 minutes to 45 minutes).

Each alert will create a slack notice that allows you to promote to case or ignore the alert for 30 minutes from within Slack instead of going to the Hive interface. When promoting a case, Slack will link you to the imported case, when ignoring, the alert won't re-alert at 45 / 60 minutes for 30 minutes.

A log record is generated each time which allows you to track and audit events.

## Installation:

To do:

Create a slack application to receive messages to your workspace <br>
Create a "echo" twimlet to playback a custom voice message when called by Twilio: https://www.twilio.com/labs/twimlets/echo <br>
Create a twilio account to receive calls / sms's

1. Install Python Virtual Environment ```python3 -m venv env```
2. Activate Virtual Environment ``` . env/bin/activate```
3. Install dependencies ```pip install -r requirements.txt```
4. Add in custom variables in ```configuration.py``` which is injected into the main application at runtime.
5. Run using ```python bot.py``` - if you wish to run as a service, see below:

It's recommended to setup a reverse proxy to forward requests to your flask server running on port 3000. Here's a mini example using Nginx - this is not production ready:

```
server {
  listen 80;
  server_name super_cool.server.com;

  access_log /var/log/nginx/web_api/access.log;
  error_log /var/log/nginx/web_api/error.log error
  

  location /web_api/ {
    proxy_ignore_client_abort on;
    proxy_pass http://192.168.1.2:3000/;
  }
}

```

## Create sysinitv service on Linux:

Place in ```/etc/systemd/system/thehive_sla_monitor.service```
```
[Unit]
Description=TheHive SLA Monitor

[Service]
Type=simple
ExecStart=/path/to/dir/venv/bin/python /path/to/dir/bot.py
WorkingDirectory=/path/to/dir/

[Install]
WantedBy=sysinit.target
```

Reload the daemon

```systemctl daemon-reload```

You can then run the bot with ```service thehive_sla_monitor start``` on Debian systems.

## Recommendation:

I recommend setting up SSL on your website as well and ideally should only be accessible within your internal network. Setting this up is outside the scope of this readme.

If you don't wish to use a webserver for now - you can use ngrok.com to tunnel - I discourage using this for production use - https://ngrok.com/docs
