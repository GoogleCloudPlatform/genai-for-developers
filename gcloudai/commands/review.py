import click
from gcloudai.util.file_processor import format_files_as_string
from vertexai.language_models import CodeChatModel, ChatModel
import vertexai
from vertexai.preview.language_models import CodeGenerationModel


parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

@click.command(name='code')
@click.option('-c', '--context', required=False, type=str, default="")
def code(context):
    click.echo('code')
    
    source='''
CODE:
{}

'''
    qry='''
INSTRUCTIONS:
You are a staff level programmer and a software architect doing a code review.
Find inefficiencies and poor coding practices in the code. 
For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.
Pose the output as suggestions or questions
If no significant issues are found output "No Issues"
'''

    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=source, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")


@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def performance(context):
    click.echo('performance')
    
    source='''
CODE:
{}

'''
    qry='''
INSTRUCTIONS:
You are an experienced staff level programmer and an application performance tuning expert doing a code review.
Find language specific performance issues in the code, such string concatenation, as memory leaks, race conditions, and deadlocks. 
For each issue provide detailed explanation.
Output the findings with class and method names followed by the found issues.

'''
    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=source, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")


@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def security(context):
    click.echo('simple security')

    source='''
CODE: 
{}
'''
    qry='''
    INSTRUCTIONS:
You are an experienced security programmer doing a code review. Looking for security violations in the code.
Examine the attached code for potential security issues. Issues to look for, look for instances of insecure cookies, insecure session management, any instances of SQL injection, cross-site scripting (XSS), 
or other vulnerabilities that could compromise user data or allow unauthorized access to the application. 
Provide a comprehensive report of any identified vulnerabilities and recommend appropriate remediation measures.
Output the findings with class and method names followed by the found issues.

Example of the output format to use:
Class name.Method name: 
Issue: 
Recommendation: 

If no issues are found, output "No issues found".
'''
    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=source, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")
    



@click.group()
def review():
    pass

review.add_command(code)
review.add_command(performance)
review.add_command(security)