import os
import subprocess
import requests

from git import Repo
from github import Auth

from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_google_vertexai import ChatVertexAI
from google.cloud.aiplatform import telemetry
from vertexai.generative_models import GenerativeModel

from .constants import USER_AGENT, MODEL_NAME
from .file_processor import format_files_as_string


github = GitHubAPIWrapper(
    github_app_id=os.getenv("GITHUB_APP_ID"),
    github_app_private_key=os.getenv("GITHUB_APP_PRIVATE_KEY"),
    github_repository=f"{os.getenv('GITHUB_ACCOUNT')}/{os.getenv('REPO_NAME')}",
)

model = GenerativeModel(MODEL_NAME)

file_update_request = """{}
OLD <<<<
{}
>>>> OLD
NEW <<<<
{}
>>>> NEW
"""


def get_source_code(repo_name: str):
    github_account = os.environ["GITHUB_ACCOUNT"]
    repo_name = os.environ["REPO_NAME"]

    clone_repo(github_account, repo_name)
    return format_files_as_string(f"{repo_name}")


def generate_pr_summary(existing_source_code: str, new_source_code: str) -> str:
    pr_summary_template = """
    Summarize the changes between old and new source code and return summary for GitHub pull request. 
    Response format: PR Name\nnPR description
    Example format: Test PR\nnThis is a test PR.

    OLD SOURCE CODE:
    {}

    NEW SOURCE CODE:
    {}
    """

    try:
        with telemetry.tool_context_manager(USER_AGENT):
            code_chat = model.start_chat(response_validation=False)
            pr_response = code_chat.send_message(
                pr_summary_template.format(existing_source_code, new_source_code)
            )
            return pr_response.text
    except Exception as e:
        print(f"Error generating pull request summary: {e}")
        return


def create_github_pr(branch: str, files: dict[str, str]):
    """Opens new GitHub Pull Request with updated files
    Args:
    branch (str): branch name.
    files (dict[str, str]): file path and content pairs
    """

    try:
        resp = github.create_branch(branch)
        print(resp)
    except Exception as e:
        print(f"Error creating branch: {e}")
        return

    existing_files = {}
    existing_source_code = ""
    new_source_code = ""

    for filepath, content in files.items():
        try:
            old_file_contents = github.read_file(filepath)
            existing_files[filepath] = old_file_contents

            resp = github.update_file(
                file_update_request.format(filepath, old_file_contents, content)
            )
            print(resp)

            existing_source_code += f"\nFile: {filepath}\nContent:\n{old_file_contents}"
            new_source_code += f"\nFile: {filepath}\nContent:\n{content}"
        except Exception as e:
            print(f"Error updating file {filepath}: {e}")
            return

    try:
        pr_summary = generate_pr_summary(existing_source_code, new_source_code)
        resp = github.create_pull_request(pr_summary)
        print(resp)
        return resp
    except Exception as e:
        print(f"Error creating pull request: {e}")
        return

def clone_repo(github_account: str, repo_name: str):
    
    try:
        github_app_id = os.environ["GITHUB_APP_ID"]
        github_installation_id = os.environ["GITHUB_APP_INSTALLATION_ID"]
        github_app_private_key = os.environ["GITHUB_APP_PRIVATE_KEY"]

        try:
            with open(github_app_private_key, "r") as f:
                private_key = f.read()
        except Exception:
            private_key = github_app_private_key

        auth = Auth.AppAuth(
            github_app_id,
            private_key,
        )
        
        jwt_token = auth.create_jwt()
        
        response = requests.post(
            f"https://api.github.com/app/installations/{github_installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
            },
        )

        installation_token = response.json()["token"]

        repo = Repo.clone_from(
            f"https://x-access-token:{installation_token}@github.com/{github_account}/{repo_name}.git",
            repo_name,
        )

        return repo

    except Exception as e:
        print(f"Error cloning repository: {e}")
        return None


def delete_folder(repo_name: str):
    try:
        subprocess.run(["rm", "-rf", repo_name], check=True)
    except Exception as e:
        print(f"Error deleting folder: {e}")
    

def create_pull_request(prompt: str):

    response = ""
    try:
        repo_name = os.environ["REPO_NAME"]

        delete_folder(repo_name)

        source_code = get_source_code(repo_name)

        summary = get_summary(README_UPDATE_INSTRUCTIONS, source_code)

        branch = "feature/docs-update"
        file = "README.md"

        response = create_github_pr(
            branch,
            {
                file: summary,
            },
        )
        return response
    except Exception as e:
        print(f"Failed to create pull request: {e}")
    finally:
        delete_folder(repo_name)

    return response

def get_summary(instructions, source_code):
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = model.start_chat(response_validation=False)
        code_chat.send_message(instructions)
        response = code_chat.send_message(source_code)
    return response.text



README_UPDATE_INSTRUCTIONS = """### Instruction ###
Generate a comprehensive README.md file for the provided context. The README should follow industry best practices and be suitable for professional developers. Resources like dora.dev, stc.org, and writethedocs.org should be used as guidelines.

It should be clear, concise, and easy to read written in a professional mannor conveying the project's purpose and value effectively.

### Output Format ### 
A well-structured README.md file in Markdown format. The README, using markdown formatting,  should include the following sections (at a minimum):

Description
Table of Contents
Features
Installation
Usage
Contributing
License
Contact

### Example Dialogue ###
Instruction:
Generate a comprehensive README.md file for the provided project. The README should follow industry best practices and be suitable for professional developers.

Context (project):
Project Name: Cymbal Coffee
Description: A Python library for data analysis and visualization, designed to simplify common data wrangling tasks and generate insightful plots.
Technologies Used: Python, Pandas, NumPy, Matplotlib, Seaborn
Features:
* Easy data loading from various sources (CSV, Excel, SQL, etc.)
* Powerful data cleaning and transformation functions
* Interactive data exploration with summary statistics and filtering
* Customizable visualization templates for common plot types
* Integration with Jupyter Notebooks for seamless analysis
Installation: pip install cymbal
Usage: See examples in the 'examples' directory or visit our documentation: [link to documentation]
Contribution Guidelines: We welcome contributions! Please follow our style guide and submit pull requests for review.
License: Apache 2.0 License
Contact Information: Email us at support@cymbal.coffee or open an issue on our GitHub repository.
"""