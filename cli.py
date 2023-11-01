import click
import os
from vertexai.language_models import CodeChatModel, ChatModel
from google.cloud import aiplatform
from gcloudai.commands import cmd

def send_message(prompt, context):
    code_chat_model = ChatModel.from_pretrained("chat-bison")
    
    if context == "":
        ignore_dirs = ["__pycache__", ".venv", ".vscode"]
        
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
def query(query, context):
    click.echo('Calling Chat with Context')
    response = send_message(query, context)
    click.echo(response)

cli.add_command(ai)
cli.add_command(query)
cli.add_command(cmd.hello)


if __name__ == '__main__':
    cli()