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
from git import Repo

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper

from google.cloud.aiplatform import telemetry
from langchain_google_vertexai import ChatVertexAI
from vertexai.generative_models import GenerativeModel

from .github_utils import delete_folder
from .constants import USER_AGENT, MODEL_NAME
from .file_processor import format_files_as_string


LLM_INSTRUCTION_TEMPLATE = """You are principal software engineer and given requirements below for implementation.
        You must follow rules when generating implementation:
        - you must use existing codebase from the context below
        - in your response, generate complete source code files and not diffs
        - in your response, include full filepath with name before file content, excluding repository name
        - must return response using sample format
        
        REQUIREMENTS:
        {prompt}

        SAMPLE RESPONSE FORMAT:
        menu-service/src/main/java/org/google/demo/Menu.java
        OLD <<<<
        existing code from the context below for the file
        >>>> OLD
        NEW <<<<
        new generated code by LLM
        >>>> NEW

        CONTEXT:
        {codebase}
        """

PR_PROMPT_TEMPLATE = """Create GitLab merge request using provided details below.
        Update existing files or Create new files, commit them and push them to opened merge request.
        
        DETAILS: 
        {response_text}
        """

class MergeRequestError(Exception):
    """Custom exception for merge request creation."""
    pass

def _create_branch() -> str:
    """Creates a new branch in GitLab for a merge request.

    Returns:
        str: The name of the newly created branch.
    """
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

def _clone_repo(repo_name: str) -> Repo:
    """Clones a GitLab repository to the local file system.

    Args:
        repo_name (str): The name of the repository to clone.

    Returns:
        Repo: The cloned repository object.
    """
    gitlab_repo_name = os.environ["GITLAB_REPOSITORY"]
    gitlab_access_token = os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"]

    repo = Repo.clone_from(
        f"https://oauth2:{gitlab_access_token}@gitlab.com/{gitlab_repo_name}.git",
        repo_name,
    )

    return repo

def _init_agent(new_gitlab_branch: str):
    """Initializes an agent with the GitLab toolkit.

    Args:
        new_gitlab_branch (str): The name of the branch to use for the agent.

    Returns:
        Agent: The initialized agent.
    """
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
        max_iterations=10,
        return_intermediate_steps=True,
        early_stopping_method="generate",
    )

    return agent

def _generate_llm_instructions(prompt: str, codebase: str) -> str:
    """Generates instructions for the Language Model (LLM).

    Args:
        prompt (str): The user prompt.
        codebase (str): The codebase context.

    Returns:
        str: The formatted instructions for the LLM.
    """
    return LLM_INSTRUCTION_TEMPLATE.format(prompt=prompt, codebase=codebase)

def _get_llm_response(instructions: str, repo_name: str) -> str:
    """Sends instructions to the LLM and retrieves its response.

    Args:
        instructions (str): The instructions for the LLM.
        repo_name (str): The name of the repository.

    Returns:
        str: The response from the LLM.
    """
    code_chat_model = GenerativeModel(MODEL_NAME)

    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat(response_validation=False)
        response = code_chat.send_message(instructions)
    
    # Remove repo name from the response
    return response.text.replace(f"{repo_name}/", "")

def _create_gitlab_merge_request(response_text: str, agent) -> None:
    """Creates a GitLab merge request using the provided response text and agent.

    Args:
        response_text (str): The response text to use for the merge request.
        agent: The agent to use for creating the merge request.
    """
    pr_prompt = PR_PROMPT_TEMPLATE.format(response_text=response_text)
    agent.invoke(pr_prompt)

def create_merge_request(prompt: str) -> str:
    """Creates a new GitLab merge request.

    Args:
        prompt (str): The prompt describing the changes to be made.

    Returns:
        str: The implementation details returned by the LLM.

    Raises:
        MergeRequestError: If an error occurs during the merge request creation.
    """
    _, repo_name = get_repo_details()
    try:
        delete_folder(repo_name)    
        _clone_repo(repo_name)
        codebase = load_codebase(repo_name, prompt)

        instructions = _generate_llm_instructions(prompt, codebase)
        implementation_details = _get_llm_response(instructions, repo_name)

        new_gitlab_branch = _create_branch()
        agent = _init_agent(new_gitlab_branch)
        
        _create_gitlab_merge_request(implementation_details, agent)
        
        return implementation_details
    except Exception as e:
         raise MergeRequestError(f"Failed to create merge request: {e}") from e
    finally:
        delete_folder(repo_name)

def get_repo_details() -> tuple[str, str]:
    """Extracts the repository owner and name from the GITLAB_REPOSITORY environment variable.

    Returns:
        tuple[str, str]: A tuple containing the repository owner and name.
    """
    gitlab_repo_name = os.environ["GITLAB_REPOSITORY"]
    repo = gitlab_repo_name.split("/")
    return (repo[0], repo[1])

def load_codebase(repo_name: str, prompt: str) -> str:
    """Loads the codebase from the specified repository.

    Args:
        repo_name (str): The name of the repository.
        prompt (str): The user prompt.

    Returns:
        str: The formatted codebase as a string.
    """
    # Defaults to repo root
    service = ""

    if "menu service" in prompt.lower():
        service = "menu-service"
    if "customer service" in prompt.lower():
        service = "customer-service/src"
    if "customer ui" in prompt.lower():
        service = "customer-ui/src"
    if "inventory service" in prompt.lower():
        service = "inventory-service/spanner"
    if "order-service" in prompt.lower():
        service = "order-service"

    code_path = f"{repo_name}/{service}"

    return format_files_as_string(code_path)
