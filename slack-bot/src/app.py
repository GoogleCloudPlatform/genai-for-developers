import os
# Use the package we installed
from slack_bolt import App
from vertexai.language_models import CodeChatModel, ChatModel


# Initialize your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# New functionality


@app.event("message")
def echo_message(client, event, logger):
   print(event)
   code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
   context = "SYSTEM: You are a slackbot proficient in all coding languages. You specialize in development for Google Cloud. Respond ONLY to coding related questions. For non technical questions reply with 'I Don't know how to answer that, I can only answer coding related technical questions'. Ensure all responses are appropriate for a slackbot."
   chat = code_chat_model.start_chat(context=context)
   response = chat.send_message(event["text"])

   client.chat_postMessage(channel=event["channel"], text=response.text)

# Listen for a button invocation with action_id `button_abc`


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
        # the user that opened your app's app home
        user_id=event["user"],
        # the view object that appears in the app home
        view={
            "type": "home",
            "callback_id": "home_view",

            # body of the view
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome to your _App's Home tab here_* :tada:"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Click me!"
                            }
                        }
                    ]
                }
            ]
        }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")


# Ready? Start your app!
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
