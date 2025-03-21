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
from vertexai.generative_models import GenerativeModel
from devai.commands.constants import MODEL_NAME

@click.command()
@click.option('-q', '--qry', required=False, type=str, default="Hello")
def with_msg_streaming(qry):
    """Send a prompt to Gemini with streaming response."""
    click.echo("Prompt with streaming")
    
    # Initialize Gemini
    model = GenerativeModel(MODEL_NAME)
    
    # Send the prompt and stream response
    responses = model.generate_content(qry, stream=True)
    for response in responses:
        click.echo(response.text, nl=False)