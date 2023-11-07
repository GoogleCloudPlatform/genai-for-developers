import click
from gcloudai.util.file_processor import format_files_as_string
from vertexai.language_models import CodeChatModel, ChatModel
import vertexai
from vertexai.preview.language_models import CodeGenerationModel

# vertexai.init(project="genai-cicd", location="us-central1")


parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.
}

@click.command(name='efficiency')
@click.option('-c', '--context', required=False, type=str, default="")
def efficiency(context):
    click.echo('efficiency')
    
    prompt='''
You are an experienced programmer and a software architect doing a code review.
Find inefficiencies in the code. For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.

Code: {}
'''
    context=format_files_as_string(context)

   
    model = CodeGenerationModel.from_pretrained("code-bison-32k")
    response = model.predict(
        prefix = prompt.format(context),
        **parameters
    )
    click.echo(f"Response from Model: {response.text}")
    





@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def performance(context):
    click.echo('performance')

    prompt='''
You are an experienced programmer and an application performance tuning expert doing a code review.
Find performance issues in the code. For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.

Code: {}
'''
    context=format_files_as_string(context)

    model = CodeGenerationModel.from_pretrained("code-bison-32k")
    response = model.predict(
        prefix = prompt.format(context),
        **parameters
    )
    click.echo(f"Response from Model: {response.text}")
    





@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def secrets(context):
    click.echo('secrets')

    prompt='''
You are an experienced SIEM programmer doing a code review. Looking for policy violations in the code.
You MUST find policy violations using examples below. For each issue provide a detailed explanation.
Policy violation examples:
- hardcoded passwords and secret key
- using IPs addresses vs DNS
- using http or ftp vs https or ftps protocols. example http:// or ftp://

Output the findings with class and method names followed by the found issues.

Code: {}
'''
    context=format_files_as_string(context)

    model = CodeGenerationModel.from_pretrained("code-bison-32k")
    response = model.predict(
        prefix = prompt.format(context),
        **parameters
    )
    click.echo(f"Response from Model: {response.text}")
    



@click.group()
def review():
    pass

review.add_command(efficiency)
review.add_command(performance)
review.add_command(secrets)