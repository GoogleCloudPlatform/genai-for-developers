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
import sys

from devai.util.file_processor import format_files_as_string, list_files, list_changes, list_commit_messages, list_commits_for_branches, list_tags, list_commits_for_tags


@click.command(name="report")
@click.option('-t', '--tag', required=True, type=str)
def report(tag):
    click.echo('report')
    click.echo(f'tag={tag}')

    response = summary_for_tag(tag, report_qry)

    click.echo(f"Response from Model:\n{response.text}")


@click.command(name="notes")
@click.option('-t', '--tag', required=True, type=str)
def notes(tag):
    click.echo('notes')
    click.echo(f'tag={tag}')

    response = summary_for_tag(tag, user_notes_qry)

    click.echo(f"Response from Model:\n{response.text}")


def check_if_string_is_in_list(string, list):
  for item in list:
    if string == item:
      return True

  return False


def summary_for_tag(tag, qry):
    tags = list_tags()
    

    if len(tags) == 0:
        click.echo("No tags found")
        sys.exit()

    if not check_if_string_is_in_list(tag, tags):
        click.echo(f"Tag {tag} does not exist. Existing tags: {tags}")
        sys.exit()

    previous_tag = ""
    list = []

    refer_commit_parent = False
    if len(tags) == 1 or tag == tags[0]:
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
    commit_messages = list_commit_messages(
        start_sha, end_sha, refer_commit_parent)

    # Format the source prompt with the data
    prompt_context = source.format(
        changes, commit_messages, format_files_as_string(files))

    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    chat = code_chat_model.start_chat(context=prompt_context, **parameters)
    
    response = chat.send_message(qry)

    return response


@click.group()
def release():
    pass


release.add_command(report)
release.add_command(notes)
