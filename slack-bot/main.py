# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import logging
import os

from vertexai.language_models import CodeChatModel, ChatModel
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.event("message")
def echo_message(client, event, logger):
   print(event)
   code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
   context = "SYSTEM: You are a slackbot proficient in all coding languages. You specialize in development for Google Cloud. Respond ONLY to coding related questions. For non technical questions reply with 'I Don't know how to answer that, I can only answer coding related technical questions'. Ensure all responses are appropriate for a slackbot."
   chat = code_chat_model.start_chat(context=context)
   response = chat.send_message(event["text"])

   client.chat_postMessage(channel=event["channel"], text=response.text)



flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Only for local debug
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0",
                  port=int(os.environ.get("PORT", 3000)))
