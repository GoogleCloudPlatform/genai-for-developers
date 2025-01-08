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

import datetime
import gitlab
import os

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper

from google.cloud.aiplatform import telemetry
from langchain_google_vertexai import ChatVertexAI

from .constants import USER_AGENT, MODEL_NAME

def create_branch():
    """Creates new branch for merge request"""

    gitlab_url = os.environ["GITLAB_URL"]
    gitlab_base_branch = os.environ["GITLAB_BASE_BRANCH"]
    gitlab_repo_name = os.environ["GITLAB_REPOSITORY"]
    gitlab_access_token = os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"]

    gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_access_token)
    project = gl.projects.get(gitlab_repo_name)

    new_branch_name = f'feature/generated-{datetime.datetime.now().strftime("%m%d%Y-%H%M")}'
    project.branches.create({'branch': new_branch_name, 'ref': gitlab_base_branch})
    print("Created new branch:", new_branch_name)

    return new_branch_name

def init_agent():
    """Initializes agent with GitLab toolkit"""

    new_gitlab_branch = create_branch()
    gitlab = GitLabAPIWrapper(gitlab_branch=new_gitlab_branch)
    toolkit = GitLabToolkit.from_gitlab_api_wrapper(gitlab)

    with telemetry.tool_context_manager(USER_AGENT):
        llm = ChatVertexAI(model_name=MODEL_NAME,
            convert_system_message_to_human=True,
            temperature=0.2,
            max_output_tokens=8192)

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

    return agent

def create_merge_request(details: str):
    """Creates new GitLab merge request"""

    pr_prompt = f"""Create GitLab merge request using provided details below.
    Create new files, commit them and push them to opened merge request.
    When creating new files, remove the lines that start with ``` before saving the files.

    DETAILS: 
    {details}
    """

    agent = init_agent()
    agent.invoke(pr_prompt)