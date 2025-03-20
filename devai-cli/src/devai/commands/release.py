# Copyright 2024 Google LLC
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
import os
import subprocess
from devai.util.file_processor import (
    format_files_as_string,
    list_files,
    list_changes,
    list_commit_messages,
    list_commits_for_branches,
    list_tags,
    list_commits_for_tags
)
from vertexai.generative_models import GenerativeModel
from devai.util.constants import GEMINI_PRO_MODEL

MODEL_NAME = GEMINI_PRO_MODEL

parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

source = '''
GIT DIFFS:
{}

GIT COMMITS:
{}

FINAL CODE:
{}

'''
report_qry = '''
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

Using this pattern, analyze provided GIT DIFFS, GIT COMMITS and FINAL CODE section 
and write technical summary about what has changed in several sentences with bullet points.
Use technical tone for explanation.
Only write explanation for new code changes and not for existing code in the FINAL CODE section.
'''

user_notes_qry = '''
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

Using this pattern, analyze provided GIT DIFFS, GIT COMMITS and FINAL CODE section 
and write end user summary about what has changed in several sentences with bullet points.
Use user humorous tone for explanation. MUST INCLUDE ONE JOKE
Only write explanation for new code changes and not for existing code in the FINAL CODE section.
'''


def check_git_environment():
    """Check if we're in a valid git environment.
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                      check=True, capture_output=True, text=True)
        
        # Check if git is configured
        subprocess.run(['git', 'config', '--get', 'user.name'], 
                      check=True, capture_output=True)
        subprocess.run(['git', 'config', '--get', 'user.email'], 
                      check=True, capture_output=True)
        
        return True, ""
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
        if "not a git repository" in stderr:
            return False, "Not a git repository. Please run this command from a git repository."
        elif "user.name" in stderr or "user.email" in stderr:
            return False, "Git user configuration missing. Please configure git user.name and user.email."
        else:
            return False, f"Git environment check failed: {stderr}"


@click.command(name="report")
@click.option('-t', '--tag', required=True, type=str)
def report(tag):
    """Generate a technical report of changes between tags."""
    click.echo('report')
    click.echo(f'tag={tag}')

    # Check git environment
    is_valid, error_msg = check_git_environment()
    if not is_valid:
        click.echo(f"Error: {error_msg}")
        sys.exit(1)

    response = summary_for_tag(tag, report_qry)

    click.echo(f"Response from Model:\n{response}")


@click.command(name="notes_user_tag")
@click.option('-t', '--tag', required=True, type=str)
def notes(tag):
    """Generate user-friendly release notes between tags."""
    click.echo('notes')
    click.echo(f'tag={tag}')

    # Check git environment
    is_valid, error_msg = check_git_environment()
    if not is_valid:
        click.echo(f"Error: {error_msg}")
        sys.exit(1)

    response = summary_for_tag(tag, user_notes_qry)

    click.echo(f"Response from Model:\n{response}")


def check_if_string_is_in_list(string, list):
  for item in list:
    if string == item:
      return True

  return False


def get_model():
    """Get the Gemini model instance."""
    return GenerativeModel(MODEL_NAME)


def summary_for_tag(tag, qry):
    """Generate a summary of changes between tags."""
    tags = list_tags()

    if len(tags) == 0:
        click.echo("No tags found")
        sys.exit(1)

    if not check_if_string_is_in_list(tag, tags):
        click.echo(f"Tag {tag} does not exist. Existing tags: {tags}")
        sys.exit(1)

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
    commit_messages = list_commit_messages(start_sha, end_sha, refer_commit_parent)

    # Format the prompt with all context
    prompt = f"""
{qry}

Context:
{source.format(changes, commit_messages, format_files_as_string(files))}
"""

    # Initialize Gemini and generate response
    model = get_model()
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": parameters["max_output_tokens"],
            "temperature": parameters["temperature"]
        }
    )

    return response.text


@click.group()
def release():
    """Commands for generating release notes and reports."""
    pass


release.add_command(report)
release.add_command(notes)
