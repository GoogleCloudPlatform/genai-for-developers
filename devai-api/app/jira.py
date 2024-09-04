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

with telemetry.tool_context_manager(USER_AGENT):
    llm = ChatVertexAI(model_name=MODEL_NAME,
                    convert_system_message_to_human=True,
                    project=os.environ["PROJECT_ID"],
                    location=os.environ["LOCATION"],
                    temperature=0.2,
                    max_output_tokens=8192)

jira = JiraAPIWrapper()
toolkit = JiraToolkit.from_jira_api_wrapper(jira)
agent = initialize_agent(
    toolkit.get_tools(), 
    llm, 
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=True,
    early_stopping_method="generate",
)


def create_issue(description: str) -> str:
    """Creates a Jira issue"""
    JIRA_USERNAME = os.environ["JIRA_USERNAME"]
    JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
    JIRA_INSTANCE_URL = os.environ["JIRA_INSTANCE_URL"]
    JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]

    summary = "Issue {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    issue_type = "Task"
    project_key=JIRA_PROJECT_KEY
    jira = JIRA(basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN), server=JIRA_INSTANCE_URL)

    issue_dict = {
        'project': {'key': project_key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type},
        
    }
    new_issue = jira.create_issue(fields=issue_dict)
    resp = f'New issue created with key: {new_issue.key}'
    
    print(resp)
    return resp

create_issue_tool = StructuredTool.from_function(create_issue, description="Create a new JIRA issue")

create_agent = initialize_agent(
    [create_issue_tool],
    llm,
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
    create_prompt = """Create a new JIRA issue with description below:
                 CONTENT:
                 {}""".format(json.dumps(context))

    cleaned_prompt = create_prompt.strip()
    cleaned_prompt = cleaned_prompt.replace("```", "{code}")   

    return create_agent(cleaned_prompt)


@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def create(context):
    return create_jira_issue("Jira Issue Summary", context)
    

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def fix(context):

    prompt = """
        INSTRUCTIONS:
        You are principal software engineer and given requirements to implement.
        Please provide implementation details and documentation.
        
        CONTEXT:
        {}
        """.format(context)

    fix = llm.invoke(
        prompt
    )

    create_prompt = """Create a new JIRA issue with description below:
                 CONTENT:
                 {}""".format(json.dumps(fix.content))

    cleaned_prompt = create_prompt.strip()
    cleaned_prompt = cleaned_prompt.replace("```", "{code}")    

    create_agent(cleaned_prompt)

@click.group()
def jira():
    pass

jira.add_command(list)
jira.add_command(fix)
jira.add_command(create)
