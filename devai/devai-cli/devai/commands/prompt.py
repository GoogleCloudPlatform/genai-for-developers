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

from devaicore.prompt import basic



@click.command(name='simple')
@click.option('-q', '--query', required=False, type=str, default="Provide a summary of this source code")
@click.option('-c', '--context', required=False, type=str, default="")
def simple(query, context):
    click.echo("Simple Prompt")

    response = basic(query=query, context=context)

    click.echo(response)



@click.group()
def prompt():
    pass

prompt.add_command(simple)

