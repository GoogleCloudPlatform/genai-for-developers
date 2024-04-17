# Copyright 2023 Google LLC
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


from vertexai.language_models import CodeChatModel, ChatModel


def basic(query, context):
    print("Prompt with context")
    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
  
    chat = code_chat_model.start_chat(context=context)
    response = chat.send_message(query)
    
    return response.text





