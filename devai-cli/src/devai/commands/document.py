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


USER_AGENT = 'cloud-solutions/genai-for-developers-v1.0'
model_name="gemini-1.5-pro"


@click.command(name='readme')
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def readme(context):
    """Create a README based on the context passed!"""
    click.echo('Create a README.md file')

@click.command(name='update-readme')
@click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_readme(context):
    """Ureate a release notes based on the context passed!
    
    
    
    
    """
    click.echo('Update README')



@click.command(name='releasenotes')
@click.option('-v', '--version', type=str, help="The version number for the release notes.")
@click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def releasenotes(context):
    """Create a release notes based on the context passed!
    
    
    
    
    """
    click.echo('update release notes')


@click.command(name='update-releasenotes')
@click.option('-v', '--version', type=str, help="The version number for the release notes.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_releasenotes(context):
    """Update release notes based on the context passed!
    
    
    
    
    """
    click.echo('create release notes')


@click.group()
def document():
    """
    Generate documentation for your project usnig GenAI.
    """
    pass

document.add_command(readme)
document.add_command(update_readme)
document.add_command(releasenotes)
document.add_command(update_releasenotes)
