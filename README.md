# afterhours_soc_bot
Runs as a service, queries Hive alerts based on a severity status. Cross checks SLA agreements and calls / SMS's the person on shift to attend to the alert. Integrates with Slack, Twilio and TheHive


1. Install requirements ```pip install -r requirements```
2. Edit variables in ```bot.py``` and ```soc_bot/templates.py```
3. Run using ```python bot.py``` - if you wish to run as a service, see below:

I recommend you setup a nginx reverse proxy to forward requests to your Flask server running on port 3000

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

I recommend setting up SSL on your website as well and ideally should only be acessible within your internal network. Setting this up is outside the scope of this readme.

If you don't wish to use nginx / apache for now - you can use ngrok.com - I discourage using this for production use unless you have a business account and can somewhat lock this down using IP whitelisting and password protection (not paid for feature). https://ngrok.com/docs

# Setting up as a python sysint service:

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
