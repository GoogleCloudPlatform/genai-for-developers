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
import re
from pathlib import Path
from typing import List, Dict

from .constants import USER_AGENT, MODEL_NAME
from .utils import get_llm, check_required_env_vars

with telemetry.tool_context_manager(USER_AGENT):
    llm = ChatVertexAI(model_name=MODEL_NAME,
                    convert_system_message_to_human=True,
                    project=os.environ["PROJECT_ID"],
                    location=os.environ["LOCATION"])

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
    project_key = os.environ["JIRA_PROJECT_KEY"]
    agent("""
    INSTRUCTIONS:
    Only read data - do not try to create/write/update any data.
    
    List JIRA tickets in the project {}. Use JQL query 'project = {}' to get the tickets.
    Print/format output as a list with ticket number use template below, description and summary.
    Example:
    Issue-1: Issue Description # 1
    Issue-2: Issue Description # 2
    """.format(project_key, project_key))

def create_jira_issue(summary, context):
    """Creates a Jira issue"""
    return create_agent("""Create a new JIRA issue with following description. 
                 DESCRIPTION:
                 {}""".format(context))

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def create(context):
    return create_jira_issue("Jira Issue Summary", context)

def get_issue_details(issue_key: str) -> dict:
    """Get details of a Jira issue"""
    check_required_env_vars()
    JIRA_USERNAME = os.environ["JIRA_USERNAME"]
    JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
    JIRA_INSTANCE_URL = os.environ["JIRA_INSTANCE_URL"]
    
    jira = JIRA(basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN), server=JIRA_INSTANCE_URL)
    try:
        issue = jira.issue(issue_key)
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description,
            'status': issue.fields.status.name
        }
    except Exception as e:
        raise click.ClickException(f"Failed to get issue details: {str(e)}")

def update_issue_status(issue_key: str, comment: str):
    """Update Jira issue status and add a comment"""
    check_required_env_vars()
    JIRA_USERNAME = os.environ["JIRA_USERNAME"]
    JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
    JIRA_INSTANCE_URL = os.environ["JIRA_INSTANCE_URL"]
    
    jira = JIRA(basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN), server=JIRA_INSTANCE_URL)
    try:
        issue = jira.issue(issue_key)
        jira.add_comment(issue, comment)
        transitions = jira.transitions(issue)
        done_transition = next((t for t in transitions if t['name'].lower() in ['done', 'resolved']), None)
        if done_transition:
            jira.transition_issue(issue, done_transition['id'])
    except Exception as e:
        raise click.ClickException(f"Failed to update issue: {str(e)}")

def parse_file_changes(implementation_text: str) -> List[Dict]:
    """Parse the LLM's response to extract file changes"""
    # Look for file paths and their content
    file_changes = []
    
    # Pattern to match file paths (common file extensions)
    file_pattern = r'`?([a-zA-Z0-9_\-./]+\.(py|yml|yaml|md|txt|json|js|ts|html|css|java|go|rb|sh))`?'
    
    # Split the text into sections (one per file)
    sections = re.split(r'\n(?=\w+[\w\s\-_]*\.(py|yml|yaml|md|txt|json|js|ts|html|css|java|go|rb|sh))', implementation_text)
    
    for section in sections:
        # Find file path
        file_match = re.search(file_pattern, section)
        if file_match:
            file_path = file_match.group(1)
            
            # Extract content between triple backticks
            content_match = re.search(r'```(?:\w+)?\n(.*?)```', section, re.DOTALL)
            if content_match:
                content = content_match.group(1).strip()
                file_changes.append({
                    'path': file_path,
                    'content': content
                })
    
    return file_changes

def implement_changes(file_changes: List[Dict]) -> List[str]:
    """Implement the file changes and return list of changes made"""
    changes_made = []
    
    for change in file_changes:
        path = Path(change['path'])
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file content
        path.write_text(change['content'])
        changes_made.append(f"- Modified {path}")
    
    return changes_made

@click.command()
@click.option('-c', '--context', required=True, type=str, help='Jira issue key (e.g., STUF-2)')
def fix(context):
    """Fix a Jira issue by implementing the required changes"""
    check_required_env_vars()
    
    # Get issue details
    issue = get_issue_details(context)
    print(f"Fixing issue {issue['key']}: {issue['summary']}")
    
    # Prepare the implementation prompt
    implementation_prompt = f"""
    You are a principal software engineer tasked with implementing a fix for the following Jira issue:
    
    Issue Key: {issue['key']}
    Summary: {issue['summary']}
    Description: {issue['description']}
    
    INSTRUCTIONS:
    1. Analyze the requirements
    2. Determine what files need to be created or modified
    3. Provide the exact file changes needed
    4. Include any necessary tests or documentation
    
    Format your response as follows:
    1. First, list all files that need to be created or modified
    2. For each file, provide the exact content or changes needed using this format:
       filename.ext
       ```
       file content here
       ```
    3. Explain any additional steps needed (e.g., commands to run)
    
    IMPORTANT: 
    - Be specific and provide actual implementation details, not just descriptions
    - Use triple backticks to denote file content
    - Include complete file content, not just changes
    """
    
    # Get implementation plan from LLM
    with telemetry.tool_context_manager(USER_AGENT):
        implementation = llm.invoke(implementation_prompt)
    
    # Parse the implementation plan and make the changes
    print("\nAnalyzing implementation plan...")
    
    try:
        # Create a new branch for the changes
        branch_name = f"fix/{issue['key'].lower()}"
        os.system(f"git checkout -b {branch_name}")
        
        # Parse and implement the changes
        file_changes = parse_file_changes(implementation.content)
        if not file_changes:
            raise click.ClickException("No file changes found in the implementation plan")
        
        print("\nImplementing changes...")
        changes_made = implement_changes(file_changes)
        
        # Commit the changes
        os.system("git add .")
        os.system(f'git commit -m "Fix {issue["key"]}: {issue["summary"]}"')
        
        # Update the issue with the changes made
        comment = f"""
        Implemented fix for {issue['key']}:
        
        Changes made:
        {chr(10).join(changes_made)}
        
        Branch: {branch_name}
        
        Please review the changes and create a merge request if satisfied.
        """
        
        update_issue_status(issue['key'], comment)
        print(f"\nSuccessfully implemented fix for {issue['key']}")
        print(f"Created branch: {branch_name}")
        print("Changes made:")
        for change in changes_made:
            print(change)
        print("\nPlease review the changes and create a merge request if satisfied.")
        
    except Exception as e:
        raise click.ClickException(f"Failed to implement fix: {str(e)}")

@click.group()
def jira():
    """Jira integration commands"""
    pass

jira.add_command(list)
jira.add_command(fix)
jira.add_command(create)
