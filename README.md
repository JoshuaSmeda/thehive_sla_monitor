## Contributing [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/JoshuaSmeda/afterhours_soc_bot/issues)

# afterhours_soc_bot
Runs as a service, queries Hive alerts based on a severity status. Cross checks SLA agreements and calls / SMS's the person on shift to attend to the alert. Integrates with Slack, Twilio and TheHive

# Outlines

This bot connects to your slack instance via the Slack API. The bot periodically polls the TheHive https://thehive-project.org/ using a API key. The bot grabs a list of alerts with a severity status of 3 (high) and performs SLA checks on the alerts (premature Hive cases). The following SLA's are outlined below:

Alerts that are older than:

30 minutes - SMS team member
45 minutes - Call team member
60 minutes - Escalate to senior

Each alert will create a slack notice that allows you to promote to case or ignore the alert for 30 minutes from within Slack and not via the Hive web interface. When promoting a case, Slack will link you to the imported case, when ignoring, the alert won't re-alert at 45 / 60 minutes for 30 minutes.

# Get setup
1. Install requirements ```pip install -r requirements```
2. Edit variables in ```bot.py``` and ```soc_bot/templates.py```
3. Create a slack app / bot - many guides on this.
4. Run using ```python bot.py``` - if you wish to run as a service, see below:

I recommend you setup a nginx reverse proxy to forward requests to your flask server running on port 3000

```
server {
  listen 443;
  server_name super_cool.server.com;

  access_log /var/log/nginx/web_api/access.log;
  error_log /var/log/nginx/web_api/error.log error
  

  location /web_api/ {
    proxy_ignore_client_abort on;
    proxy_pass http://insert_flask_ip:3000/;
  }
}

```

# Recommendations

I recommend setting up SSL on your website as well and ideally should only be acessible within your internal network. Setting this up is outside the scope of this readme.

If you don't wish to use nginx / apache for now - you can use ngrok.com - I discourage using this for production use unless you have a business account and can somewhat lock this down using IP whitelisting and password protection (not paid for feature). https://ngrok.com/docs

# Setting up as a python sysint service:

Place in ```/etc/systemd/system/soc_bot.service```
```
[Unit]
Description=SOC Bot

[Service]
Type=simple
ExecStart=/usr/bin/python /opt/soc_alerter/bot.py
WorkingDirectory=/opt/soc_alerter/

[Install]
WantedBy=sysinit.target
```

You can then run the bot with ```service soc_bot start``` on Debian for example.
