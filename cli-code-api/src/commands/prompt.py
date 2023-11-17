import click
from commands.msg import standard, streaming

from util.file_processor import get_text_files_contents
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
