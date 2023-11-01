import click
import os
from gcloudai.util.file_processor import get_text_files_contents
from vertexai.language_models import CodeChatModel, ChatModel
from google.cloud import aiplatform
from gcloudai.commands import cmd

def send_message(prompt, context):
    code_chat_model = ChatModel.from_pretrained("chat-bison")
    
    if context == "":
        ignore_dirs = ["__pycache__", "venv", ".vscode"]
        
        for root, dirs, files in os.walk('gcloudai'):
            print(".")
            # Remove directories in the ignore list from traversal
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        context += f.read() + "\n\n"  # Separate file contents with two newlines
                except UnicodeDecodeError:
                    print(f"Skipped file due to encoding error: {filepath}")
      
    chat = code_chat_model.start_chat(context=context)
    
    response = chat.send_message(prompt)
    return response.text 

@click.group()
def cli():
    pass

@click.command()
def ai():
    click.echo('Initialized AI')

@click.command()
@click.option('-q', '--query', required=False, type=str, default="Provide a summary of this source code")
@click.option('-c', '--context', required=False, type=str, default="")
def query(q, c):
    click.echo('Calling Chat with Context')
    response = send_message_with_context(q, c)
    click.echo(response)

@click.command()
def readfiles():
    click.echo('reading files')
    ignored = ["__pycache__", "venv", ".vscode", ".git"]
    text_files_contents = get_text_files_contents(".", ignore=ignored)
    
    for full_path, contents in text_files_contents.items():
        click.echo(f"File: {full_path}")
        click.echo("--------------------")
        click.echo(contents)
        click.echo("\n====================\n")

@click.command()
@click.option('-q', '--query', required=False, type=str, default="Provide a summary of this source code")
@click.option('-p', '--path', required=False, type=str, default=".")
def query2(query, path):
    code_chat_model = ChatModel.from_pretrained("chat-bison")
    #response = send_message_with_context(q, c)
    chat = code_chat_model.start_chat()

    initial_prompt='''
I'm going to provide you with a series of files individually over multiple messages. For each file do nothing other than reply with the file name, do not process any further until I'm done sending all the files.  
I will signify I'm done sending file with the following string "===LOAD COMPLETE===". Respond with confirmation that you've received the files.
Next I will ask a question about all those files.

Here are the files
'''
    

    response = chat.send_message(initial_prompt)
    click.echo("-")
    click.echo(response.text)
    ignored = ["__pycache__", "venv", ".vscode", ".git"]
    click.echo("--")
    text_files_contents = get_text_files_contents(path, ignore=ignored)
    click.echo("---")
    
    for full_path, contents in text_files_contents.items():
        click.echo(f'''
File: {full_path}
-----------------
{contents}
=================
''')
        chat.send_message(f'''
File: {full_path}
-----------------
{contents}
=================
''')
        click.echo(response.text)

    response = chat.send_message("===LOAD COMPLETE===")
    click.echo(response.text)
    response = chat.send_message(query)
    click.echo(response.text)

cli.add_command(ai)
cli.add_command(query)
cli.add_command(cmd.hello)
cli.add_command(readfiles)
cli.add_command(query2)


if __name__ == '__main__':
    cli()