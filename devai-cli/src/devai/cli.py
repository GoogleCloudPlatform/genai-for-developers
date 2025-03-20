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
from devai.commands.rag import rag
from devai.commands.healthcheck import healthcheck

# Uncomment after configuring JIRA and GitLab env variables - see README.md for details
# from devai.commands import jira
# from devai.commands import gitlab

@click.group()
def devai():
    """DevAI CLI - AI-powered development tools."""
    pass

# Register commands
devai.add_command(healthcheck)
devai.add_command(review.review)

if __name__ == '__main__':
    devai()
