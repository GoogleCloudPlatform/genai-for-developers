import click
import os
from vertexai.language_models import CodeChatModel, ChatModel
from gcloudai.commands import cmd

def send_message(prompt):
    code_chat_model = CodeChatModel.from_pretrained("codechat-bison@001")
    code_chat_model = CodeChatModel.from_pretrained("codechat-bison@001")
    code_chat_model = ChatModel.from_pretrained("chat-bison")
    # with open('hello.py', 'r') as file:
    #     context = file.read()
    ignore_dirs = ["__pycache__", ".venv", ".vscode"]
    
    context = ""
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
def query():
    click.echo('Calling Chat')
    response = send_message("Provide a summary of this source code")
    click.echo(response)

cli.add_command(ai)
cli.add_command(query)
cli.add_command(cmd.hello)


if __name__ == '__main__':
    cli()