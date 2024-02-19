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
from devai.util.file_processor import format_files_as_string, list_files, list_changes, list_commit_messages, list_commits_for_branches, list_tags, list_commits_for_tags
from vertexai.language_models import CodeChatModel


parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

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

@click.command(name="notes_user")
@click.option('-s', '--branch_a', required=True, type=str)
@click.option('-e', '--branch_b', required=True, type=str)
def notes_user(branch_a, branch_b):
    click.echo('notes_user')
    click.echo(f'branch_a={branch_a}')
    click.echo(f'branch_b={branch_b}')


    list = list_commits_for_branches(branch_a, branch_b)
    start_sha = list[len(list)-1]
    
    if len(list) == 1:
        start_sha = branch_a
        print("set start_sha to branch")

    
    end_sha = list[0]

    # This flag will enable usage of ^ operator 
    # this allows refer to the parent of a commit / include start commit in git operations(diff, log)
    refer_commit_parent = True
    files = list_files(start_sha, end_sha, refer_commit_parent)
    
    changes = list_changes(start_sha, end_sha, refer_commit_parent)
    commit_messages = list_commit_messages(start_sha, end_sha, refer_commit_parent)

    prompt_context = source.format(changes, commit_messages, format_files_as_string(files))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=prompt_context, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")

@click.command(name="notes_user_tag")
@click.option('-t', '--tag', required=True, type=str)
def notes_user_tag(tag):
    click.echo('notes_user_tag')
    click.echo(f'tag={tag}')


    
    tags = list_tags()

    if len(tags) == 0:
        click.echo("No tags found")
        return
    
    previous_tag = ""
    list = []

    refer_commit_parent = False
    if len(tags) == 1:
        list = list_commits_for_tags(tag, "HEAD")
    else:
        refer_commit_parent = True
        for i in range(len(tags)):
            if tags[i] == tag:
                previous_tag = tags[i-1]
        
        list = list_commits_for_branches(previous_tag, tag)
            
    start_sha = list[len(list)-1]
    
    if len(list) == 1:
        start_sha = previous_tag
    
    end_sha = list[0]
    
    files = list_files(start_sha, end_sha, refer_commit_parent)

    changes = list_changes(start_sha, end_sha, refer_commit_parent)

    commit_messages = list_commit_messages(start_sha, end_sha, refer_commit_parent)

    prompt_context = source.format(changes, commit_messages, format_files_as_string(files))


    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=prompt_context, **parameters)
    response = chat.send_message(qry)

    click.echo(f"Response from Model: {response.text}")

@click.group()
def release():
    pass

release.add_command(notes_user)
release.add_command(notes_user_tag)