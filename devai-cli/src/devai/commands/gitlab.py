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
from langchain.agents import AgentType, initialize_agent
from langchain_google_vertexai import ChatVertexAI
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
from google.cloud.aiplatform import telemetry
  
from .constants import USER_AGENT, MODEL_NAME

def check_required_env_vars():
    """Check for required environment variables"""
    required_vars = ['PROJECT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise click.ClickException(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them using:\n"
            f"export {' '.join(f'{var}=your-{var.lower()}' for var in missing_vars)}"
        )

def get_gitlab_agent():
    """Get or create GitLab agent"""
    project_id = os.getenv('PROJECT_ID')
    region = os.getenv('REGION', 'us-central1')
    
    llm = ChatVertexAI(model_name=MODEL_NAME,
                       convert_system_message_to_human=True,
                       project=project_id,
                       location=region)
    
    gitlab = GitLabAPIWrapper()
    toolkit = GitLabToolkit.from_gitlab_api_wrapper(gitlab)
    return initialize_agent(
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
    """Create a GitLab merge request with the given context"""
    agent = get_gitlab_agent()
    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke(f"""Create GitLab merge request, use provided details below: 
{context}""")

def create_gitlab_issue_comment(context, issue_name):
    """Create a comment on a GitLab issue"""
    agent = get_gitlab_agent()
    prompt = f"""You need to do two tasks only.
First task: Get GitLab issue with title '{issue_name}'.
Second task: add content below as a comment to the issue you found in first task:

{context}"""

    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke(prompt)

def fix_gitlab_issue_comment(context):
    """Fix a GitLab issue by creating a pull request"""
    agent = get_gitlab_agent()
    prompt = f"""You have the software engineering capabilities of a Google Principle engineer.
You are tasked with completing issues on a gitlab repository.
Please look at the open issue #{context} and complete it by creating pull request that solves the issue."""

    with telemetry.tool_context_manager(USER_AGENT):
        return agent.invoke(prompt)

@click.group()
def gitlab():
    """GitLab integration commands"""
    check_required_env_vars()

@gitlab.command()
@click.option('--context', required=True, help='Context for the merge request')
def create_pr(context):
    """Create a GitLab merge request"""
    check_required_env_vars()
    return create_pull_request(context)

@gitlab.command()
@click.option('--context', required=True, help='Comment content')
@click.option('--issue', required=True, help='Issue title to comment on')
def create_comment(context, issue):
    """Create a comment on a GitLab issue"""
    check_required_env_vars()
    return create_gitlab_issue_comment(context, issue)

@gitlab.command()
@click.option('--context', required=True, help='Issue number to fix')
def fix_issue(context):
    """Fix a GitLab issue by creating a pull request"""
    check_required_env_vars()
    return fix_gitlab_issue_comment(context)
