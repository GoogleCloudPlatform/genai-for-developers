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

from devai.commands import prompt, review, release, document
from devai.commands.healthcheck import healthcheck

# Uncomment after configuring JIRA and GitLab env variables - see README.md for details
#from devai.commands import jira  # Uncommented for testing Jira integration
# from devai.commands import gitlab  # Commented out after testing GitLab integration
# from devai.commands import github_cmd  # Commented out after testing GitHub integration

@click.group()
def devai():
    """DevAI CLI - AI-powered development tools."""
    pass

# Register commands
devai.add_command(healthcheck)
devai.add_command(review.review)
devai.add_command(prompt.prompt)
devai.add_command(document.document)
devai.add_command(release.release)
#devai.add_command(jira.jira)
# devai.add_command(gitlab.gitlab)  # Commented out after testing GitLab integration
# devai.add_command(github_cmd.github)  # Commented out after testing GitHub integration

if __name__ == '__main__':
    devai()
