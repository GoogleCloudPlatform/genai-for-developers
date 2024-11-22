import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities.github import GitHubAPIWrapper
from google.cloud.aiplatform import telemetry
from .constants import MODEL_NAME, USER_AGENT

model = ChatVertexAI(
    model_name=MODEL_NAME,
    convert_system_message_to_human=True,
    project=os.environ["PROJECT_ID"],
    location=os.environ["LOCATION"],
)

github = GitHubAPIWrapper(
    github_app_id=os.getenv("GITHUB_APP_ID"),
    github_app_private_key=os.getenv("GITHUB_APP_PRIVATE_KEY"),
    github_repository=os.getenv("GITHUB_REPOSITORY"),
)

file_update_request = """{}
OLD <<<<
{}
>>>> OLD
NEW <<<<
{}
>>>> NEW
"""

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
            pr_response = model.invoke(pr_summary_template.format(existing_source_code, new_source_code))
            return pr_response.content
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

            resp = github.update_file(file_update_request.format(filepath, old_file_contents, content))
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
    except Exception as e:
        print(f"Error creating pull request: {e}")
        return
