import click
from gcloudai.util.file_processor import format_files_as_string
from vertexai.language_models import CodeChatModel, ChatModel
import vertexai
from vertexai.preview.language_models import CodeGenerationModel

# vertexai.init(project="genai-cicd", location="us-central1")


parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

@click.command(name='efficiency')
@click.option('-c', '--context', required=False, type=str, default="")
def efficiency(context):
    click.echo('efficiency')
    
    prompt='''
CODE:
{}

INSTRUCTIONS:
You are an experienced programmer and a software architect doing a code review.
Find inefficiencies in the code. For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.


'''
    context=format_files_as_string(context)

   
    # model = CodeGenerationModel.from_pretrained("code-bison-32k")
    model = CodeGenerationModel.from_pretrained("code-bison")
    response = model.predict(
        prefix = prompt.format(context),
        **parameters
    )
    click.echo(f"Request to Model: {prompt.format(context)}")
    click.echo(f"Response from Model: {response.text}")
    





@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def performance(context):
    click.echo('performance')

    prompt='''
CODE: 
{}

INSTRUCTIONS:
You are an experienced programmer and an application performance tuning expert doing a code review.
Find performance issues in the code. For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.


'''
    context=format_files_as_string(context)

    #model = CodeGenerationModel.from_pretrained("code-bison-32k")
    model = CodeGenerationModel.from_pretrained("code-bison")
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
CODE: 
{}

INSTRUCTIONS:
You are an experienced security programmer doing a code review. Looking for security violations in the code.
You MUST find security violations using examples below. For each issue provide a detailed explanation.


Output the findings with class and method names followed by the found issues.
If no issues are found, output "No issues found".

'''
    context=format_files_as_string(context)

    # model = CodeGenerationModel.from_pretrained("code-bison-32k")
    model = CodeGenerationModel.from_pretrained("code-bison")
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