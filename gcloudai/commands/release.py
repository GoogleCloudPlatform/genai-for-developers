import click
from gcloudai.util.file_processor import format_files_as_string, list_files, list_changes, list_commit_messages
from vertexai.language_models import CodeChatModel


parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

@click.command(name="notes_user")
@click.option('-s', '--start_sha', required=True, type=str)
@click.option('-e', '--end_sha', required=True, type=str)
def notes_user(start_sha, end_sha):
    click.echo('notes_user')
    click.echo(f'start_sha={start_sha}')
    click.echo(f'end_sha={end_sha}')
    
    source='''
    GIT DIFFS:
    {}
   
    GIT COMMITS:
    {}
    
    FINAL CODE:
    {}

    '''
    qry='''
    INSTRUCTIONS:
    You are senior software engineer doing a code review. You are given following information:
    GIT DIFFS - new code changes
    GIT COMMITS - developer written comments for new code changes
    FINAL CODE - final version of the source code

    GIT DIFFS show lines added and removed with + and - indicators.
    Here's an example:
    This line shows that code was changed/removed from the FINAL CODE section:
    -            return f"file: source: [Binary File - Not ASCII Text]"
    This line shows that code was changed/added in the FINAL CODE section:
    +            # return f"file: source: [Binary File - Not ASCII Text]

    GIT COMMITS show the commit messages provided by developer that you can use for extra context.

    Using this pattern, analyze provided GIT DIFFS, GIT COMMITS and FINAL CODE section and write user friendly explanation about what has changed in several sentences with bullet points.
    Only write explanation for new code changes and not for othe code in the FINAL CODE section.
    '''

    files = list_files(start_sha, end_sha)
    changes = list_changes(start_sha, end_sha)
    commit_messages = list_commit_messages(start_sha, end_sha)

    prompt_context = source.format(changes, commit_messages, format_files_as_string(files))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=prompt_context, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")

@click.group()
def release():
    pass

release.add_command(notes_user)
