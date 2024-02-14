# Slack Client for Code Chat Bison on Vertex

Based on https://api.slack.com/start/building/bolt-python


OAuth & Permissions -> Scopes:
- calls:write
- chat:write
- im:history
- im:write
- mpim:write

Event Subscriptions -> Enable Events : URL:
- https://<host>/slack/events
Event Subscriptions -> Subscribe to bot events:
- app_home_opened
- message.im

Alternatively create and app using the manifest.json provided. Be sure to update the `request_url` first.


Teminal 2
```sh
ngrok config add-authtoken
ngrok http 3000
```

Terminal 1
```sh
python3 -m venv .venv
source .venv/bin/activate
export SLACK_BOT_TOKEN=
export SLACK_SIGNING_SECRET=
pip install google-cloud-aiplatform
pip install slack_bolt 
python3 app.py
```

