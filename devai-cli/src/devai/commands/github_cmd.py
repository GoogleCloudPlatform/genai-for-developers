import os
import click
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities.github import GitHubAPIWrapper
from google.cloud.aiplatform import telemetry
from .constants import MODEL_NAME, USER_AGENT

def check_required_env_vars():
    """Check for required environment variables"""
    required_vars = ['PROJECT_ID', 'LOCATION', 'GITHUB_APP_ID', 'GITHUB_APP_PRIVATE_KEY', 'GITHUB_REPOSITORY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise click.ClickException(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them using:\n"
            f"export {' '.join(f'{var}=your-{var.lower()}' for var in missing_vars)}"
        )

def get_github_agent():
    """Get or create GitHub agent"""
    check_required_env_vars()
    
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
    
    return model, github

file_update_request = """{}
OLD <<<<
{}
>>>> OLD
NEW <<<<
{}
>>>> NEW
"""

def generate_pr_summary(existing_source_code: str, new_source_code: str) -> str:
    """Generate a summary for a pull request comparing old and new code"""
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
        model, _ = get_github_agent()
        with telemetry.tool_context_manager(USER_AGENT):
            pr_response = model.invoke(pr_summary_template.format(existing_source_code, new_source_code))
            return pr_response.content
    except click.ClickException as e:
        # Re-raise ClickException for environment variable errors
        raise
    except Exception as e:
        print(f"Error generating pull request summary: {e}")
        return None

def create_github_pr(branch: str, files: dict[str, str]):
    """Opens new GitHub Pull Request with updated files
    Args:
    branch (str): branch name.
    files (dict[str, str]): file path and content pairs
    """
    try:
        _, github = get_github_agent()
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

@click.group()
def github():
    """GitHub integration commands"""
    pass

@github.command()
@click.option('--branch', required=True, help='Branch name for the pull request')
@click.option('--files', required=True, help='Dictionary of file paths and their contents')
def create_pr(branch, files):
    """Create a GitHub pull request"""
    try:
        files_dict = eval(files)  # Convert string representation of dict to actual dict
        create_github_pr(branch, files_dict)
    except Exception as e:
        print(f"Error creating pull request: {e}")
