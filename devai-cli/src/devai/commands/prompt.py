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
import os
import yaml
from devai.commands.msg import standard, streaming
from devai.util.file_processor import get_text_files_contents
from vertexai.language_models import CodeChatModel, ChatModel
from vertexai.generative_models import GenerativeModel
from devai.util.constants import GEMINI_PRO_MODEL

MODEL_NAME = GEMINI_PRO_MODEL

def load_prompt_template(template_path):
    """Load a prompt template from a YAML file.
    
    Args:
        template_path (str): Path to the YAML template file
        
    Returns:
        dict: The loaded template configuration
    """
    try:
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        click.echo(f"Error loading template: {e}")
        return None

def format_prompt(template, context):
    """Format a prompt template with the given context.
    
    Args:
        template (dict): The loaded template configuration
        context (str): The context to format the prompt with
        
    Returns:
        str: The formatted prompt
    """
    if not template:
        return None
        
    prompt = template['prompt']
    system_context = prompt['system_context']
    instruction = prompt['instruction']
    
    # Combine system context, instruction, and context
    return f"{system_context}\n\n{instruction}\n\n### Code Context ###\n{context}"

@click.command(name='template')
@click.option('-t', '--template-path', required=True, type=str, help="Path to the YAML template file")
@click.option('-c', '--context', required=False, type=str, default="", help="The code or context to analyze")
@click.option('-o', '--output', type=click.Choice(['markdown', 'json', 'text']), default='markdown', help="The desired output format")
def template(template_path, context, output):
    """Use a prompt template to analyze code or context.
    
    This command allows you to use predefined prompt templates to analyze code or other content.
    Templates are defined in YAML format and specify the system context, instructions, and output format.
    
    Example:
        devai prompt template -t prompts/security/web-security.yaml -c ./src/
    """
    click.echo(f"Using template: {template_path}")
    
    # Load the template
    template = load_prompt_template(template_path)
    if not template:
        return
        
    # Get context from files if directory is provided
    if os.path.isdir(context):
        ignored = ["__pycache__", "venv", ".vscode", ".git"]
        context = get_text_files_contents(context, ignore=ignored)
    
    # Format the prompt
    prompt = format_prompt(template, context)
    if not prompt:
        return
        
    # Initialize the model
    model = GenerativeModel(MODEL_NAME)
    
    # Send the prompt and get response
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.2
        }
    )
    
    # Output the response
    click.echo(response.text)

@click.command(name='with_context')
@click.option('-q', '--qry', required=False, type=str, default="Provide a summary of this source code")
@click.option('-c', '--context', required=False, type=str, default="")
def with_context(qry, context):
    """Send a prompt with code context to Gemini."""
    click.echo("Prompt with context")
    
    # Get context from files if directory is provided
    if os.path.isdir(context):
        ignored = ["__pycache__", "venv", ".vscode", ".git"]
        files_content = get_text_files_contents(context, ignore=ignored)
        # Format the files content into a readable structure
        context = "\n\n".join([
            f"File: {filepath}\n```python\n{content}\n```"
            for filepath, content in files_content.items()
        ])
    
    # Initialize Gemini
    model = GenerativeModel(MODEL_NAME)
    
    # Format the prompt with context
    prompt = f"""{qry}

Please analyze the following code:

{context}

Please provide:
1. A summary of what the code does
2. Suggestions for improvements
3. Any potential issues or concerns
4. Best practices that are being followed
"""
    
    # Send the prompt and get response
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.2
        }
    )
    click.echo(response.text)

@click.group()
def prompt():
    """
    Commands for working with prompts and templates.
    """
    pass

prompt.add_command(with_context)
prompt.add_command(streaming.with_msg_streaming)
prompt.add_command(standard.with_msg)
prompt.add_command(template)
