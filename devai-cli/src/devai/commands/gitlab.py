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
import os, json
from langchain.agents import AgentType, initialize_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
from google.cloud.aiplatform import telemetry
  
from .constants import USER_AGENT, MODEL_NAME

llm = ChatVertexAI(model_name=MODEL_NAME,
                   convert_system_message_to_human=True,
                   project=os.environ["PROJECT_ID"],
                   location=os.environ["LOCATION"])

gitlab = GitLabAPIWrapper()
toolkit = GitLabToolkit.from_gitlab_api_wrapper(gitlab)
agent = initialize_agent(
    toolkit.get_tools(), 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=True,
    early_stopping_method="generate",
)

def create_pull_request(context):
    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke("""Create GitLab merge request, use provided details below: 
    {}""".format(context))


def create_gitlab_issue_comment(context, issue_name='CICD AI Insights'):

    prompt = """You need to do two tasks only.
    First task: Get GitLab issue with title '{}'.
    Second task: add content below as a comment to the issue you found in first task:

    
    {}""".format(issue_name, json.dumps(context))

    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke(prompt)

def fix_gitlab_issue_comment(context):
    prompt = """You have the software engineering capabilities of a Google Principle engineer.
    You are tasked with completing issues on a gitlab repository.
    Please look at the open issue #{} and complete it by creating pull request that solves the issue."
    """.format(context)
    
    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke(prompt)

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def create_pr(context):
    return create_pull_request(context)

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
@click.option('-i', '--issue', required=False, type=str, default="")
def create_comment(issue, context):
    return create_gitlab_issue_comment(issue, context)

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def fix_issue(context):
    return fix_gitlab_issue_comment(context)

@click.group()
def gitlab():
    pass

gitlab.add_command(create_pr)
gitlab.add_command(create_comment)
gitlab.add_command(fix_issue)
