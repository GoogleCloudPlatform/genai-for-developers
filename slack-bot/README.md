# Slack Client for GenAI with Vertex on Google

## Installation

### Create Slack App
- Create a new app on [https://api.slack.com/apps](https://api.slack.com/apps)
- Choose from App Manifest
- Select your workspace
- Paste the following manifest into the JSON tab

```json

{
    "display_information": {
        "name": "DevAI Bot"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": false,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "DevAI Bot",
            "always_online": false
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "calls:write",
                "im:history",
                "im:write",
                "mpim:write",
                "chat:write",
                "channels:history",
                "groups:history"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://<YOUR_HOST>/slack/events",
            "bot_events": [
                "message.channels",
                "message.groups",
                "message.im"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```
- Click Create

### Save Bot Tokens
You'll need to provide credentials to Slack from the cloud run backend. 
Locate the tokens and set them as environment variables for later use. 

- Click the Basic Information link for your Slack App 
- Scroll down and locate the Signing Secret
- Click show and copy the value
- In your terminal set the env variable with the command below, pasting in your value after the equal sign
  
```sh
export SLACK_SIGNING_SECRET=
```

- Click on OAuth & Permissions in the navigation for your app in Slack
- Locate the OAuth Tokens for Your Workspace section 
- Click Install to Workspace and complete the flow
- Copy the Bot User OAuth Token
- In your terminal set the env variable with the command below, pasting in your value after the equal sign
  
```sh
export SLACK_BOT_TOKEN=
```

### Deploy Cloud Run Service

From the slack-bot directory run the following command to deploy the backing service

```sh
gcloud run deploy devai-slackbot \
    --source . \
    --allow-unauthenticated \
    --set-env-vars SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET},SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
```

- Copy the endpoint URL from the following command

```sh
echo "Slack Endpoint:"
echo "$(gcloud run services describe devai-slackbot \
    --format='value(status.url)' \
    --platform managed)/slack/events"
```

### Finalize Bot configuration

You'll need to update the backend URL for your app within the slack dashboard.

- Return to your app in [https://api.slack.com/apps](https://api.slack.com/apps)
- Click on Event SUbscriptions in the navigation.
- Paste the endpoint generated from the previous step, into the Request URL field.  
- Once the url has been verified Click Save at the bottom of the screen to persist your changes.

Now go into your slack workspace and start interacting with DevAI Bot

## Development Resources

Slack Guide: https://api.slack.com/start/building/bolt-python

UI Based Configuration: 

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

Set the following in cloudrun from [API.slack.com](https://api.slack.com/apps/A06JUDJS63C)

SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
