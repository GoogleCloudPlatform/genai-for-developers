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
import datetime
import os, json
from langchain.tools import StructuredTool
from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_google_vertexai import ChatVertexAI
from jira import JIRA
from google.cloud.aiplatform import telemetry

from .constants import USER_AGENT, MODEL_NAME

def check_required_env_vars():
    """Check for required environment variables"""
    required_vars = [
        "PROJECT_ID",
        "LOCATION",
        "JIRA_USERNAME",
        "JIRA_API_TOKEN",
        "JIRA_INSTANCE_URL",
        "JIRA_PROJECT_KEY"
    ]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise click.ClickException(f"Missing required environment variables: {', '.join(missing_vars)}")

def get_llm():
    """Get Vertex AI ChatVertexAI instance"""
    check_required_env_vars()
    with telemetry.tool_context_manager(USER_AGENT):
        return ChatVertexAI(
            model_name=MODEL_NAME,
            convert_system_message_to_human=True,
            project=os.environ["PROJECT_ID"],
            location=os.environ["LOCATION"]
        )

def get_jira_components():
    """Get Jira components (API wrapper, toolkit, and agent)"""
    check_required_env_vars()
    jira = JiraAPIWrapper()
    toolkit = JiraToolkit.from_jira_api_wrapper(jira)
    agent = initialize_agent(
        toolkit.get_tools(), 
        get_llm(), 
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=True,
        early_stopping_method="generate",
    )
    return jira, toolkit, agent

def create_issue(description: str) -> str:
    """Creates a Jira issue"""
    check_required_env_vars()
    JIRA_USERNAME = os.environ["JIRA_USERNAME"]
    JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
    JIRA_INSTANCE_URL = os.environ["JIRA_INSTANCE_URL"]
    JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]

    summary = "Issue {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    issue_type = "Task"
    project_key = JIRA_PROJECT_KEY
    jira = JIRA(basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN), server=JIRA_INSTANCE_URL)

    issue_dict = {
        'project': {'key': project_key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type},
    }
    try:
        new_issue = jira.create_issue(fields=issue_dict)
        resp = f'New issue created with key: {new_issue.key}'
        print(resp)
        return resp
    except Exception as e:
        raise click.ClickException(str(e))

def get_create_agent():
    """Get agent for creating issues"""
    check_required_env_vars()
    create_issue_tool = StructuredTool.from_function(create_issue, description="Create a new JIRA issue")
    return initialize_agent(
        [create_issue_tool],
        get_llm(),
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=True,
        early_stopping_method="generate",
    )

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def list(context):
    """List Jira issues"""
    check_required_env_vars()
    agent = get_jira_components()[2]
    agent("""
    INSTRUCTIONS:
    Only read data - do not try to create/write/update any data.
    
    List JIRA tickets in the project {}. 
    Print/format output as a list with ticket number use template below,  description and summary.
    Example:
    Issue-1: Issue Description # 1
    Issue-2: Issue Description # 2
    """.format(context))

def create_jira_issue(summary, context):
    """Creates a Jira issue"""
    check_required_env_vars()
    return get_create_agent()("""Create a new JIRA issue with following description. 
                 DESCRIPTION:
                 {}""".format(context))

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def create(context):
    """Create a new Jira issue"""
    return create_jira_issue("Jira Issue Summary", context)

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def fix(context):
    """Fix a Jira issue"""
    check_required_env_vars()
    llm = get_llm()
    prompt = """
        INSTRUCTIONS:
        You are principal software engineer and given requirements to implement.
        Please provide implementation details and documentation.
        
        CONTEXT:
        {}
        """.format(context)

    fix = llm.invoke(prompt)

    create_prompt = """Create a new JIRA issue with description below:
                 CONTENT:
                 {}""".format(json.dumps(fix.content))

    cleaned_prompt = create_prompt.strip()
    cleaned_prompt = cleaned_prompt.replace("```", "{code}")    

    get_create_agent()(cleaned_prompt)

@click.group()
def jira():
    """Jira integration commands"""
    pass

jira.add_command(list)
jira.add_command(fix)
jira.add_command(create)
