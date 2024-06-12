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

import click
from devai.commands.msg import standard, streaming

from devai.util.file_processor import get_text_files_contents
from vertexai.language_models import CodeChatModel, ChatModel


@click.command(name='with_context')
@click.option('-q', '--qry', required=False, type=str, default="Provide a summary of this source code")
@click.option('-c', '--context', required=False, type=str, default="")
def with_context(qry, context):
    click.echo("Prompt with context")
    code_chat_model = ChatModel.from_pretrained("chat-bison")

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    #context=""


    chat = code_chat_model.start_chat(context=context)
    response = chat.send_message(qry)
    
    click.echo(response.text)





@click.group()
def prompt():
    pass

prompt.add_command(with_context)
prompt.add_command(streaming.with_msg_streaming)
prompt.add_command(standard.with_msg)
