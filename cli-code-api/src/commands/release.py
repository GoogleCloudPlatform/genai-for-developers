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

import click
from util.file_processor import format_files_as_string, list_files, list_changes, list_commit_messages, list_commits_for_branches
from vertexai.language_models import CodeChatModel


parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

@click.command(name="notes_user")
@click.option('-s', '--branch_a', required=True, type=str)
@click.option('-e', '--branch_b', required=True, type=str)
def notes_user(branch_a, branch_b):
    click.echo('notes_user')
    click.echo(f'branch_a={branch_a}')
    click.echo(f'branch_b={branch_b}')
    
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

    list = list_commits_for_branches(branch_a, branch_b)

    start_sha = list[len(list)-1]
    end_sha = list[0]
    
    click.echo(f'start_sha={start_sha}')
    click.echo(f'end_sha={end_sha}')

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
