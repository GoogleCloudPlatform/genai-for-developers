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
from devai.util.file_processor import format_files_as_string
from vertexai.generative_models import (
    GenerativeModel,
    Image,
)
from google.cloud.aiplatform import telemetry
import os
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, PermissionDenied
from google.api_core.gapic_v1.client_info import ClientInfo
import logging


USER_AGENT = 'cloud-solutions/genai-for-developers-v1.0'
model_name="gemini-1.5-pro"

def ensure_env_variable(var_name):
    """Ensure an environment variable is set."""
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value

def get_prompt( secret_id: str) -> str:
    """Retrieves a secret value from Google Secret Manager.

    Args:
        secret_id: The ID of the secret to retrieve.

    Returns:
        The secret value as a string, or None if the secret is not found or the user lacks permission.
    """    
    try:
        project_id = ensure_env_variable('PROJECT_ID')
        logging.info("PROJECT_ID:", project_id)

        client = secretmanager.SecretManagerServiceClient(
        client_info=ClientInfo(user_agent=USER_AGENT)
        )
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        try:
            response = client.access_secret_version(name=name)
            payload = response.payload.data.decode("utf-8")
            logging.info(f"Successfully retrieved secret ID: {secret_id} in project {project_id}")
            return payload
        
        except PermissionDenied:
            logging.warning(f"Insufficient permissions to access secret {secret_id} in project {project_id}")
            return None
        
        except NotFound:
            logging.info(f"Secret ID not found: {secret_id} in project {project_id}")
            return None
        
        except Exception as e:  # Catching a broader range of potential errors
            logging.error(f"An unexpected error occurred while retrieving secret '{secret_id}': {e}")
            return None
    
    except EnvironmentError as e:
        logging.error(e)

@click.command(name='readme')
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def readme(context):
    """Create a README based on the context passed!
    
    This is useful when no existing README files exist. If you already have a README `update-readme` may be a better option.
    
    """
    click.echo('Generating and printing the README....')
    

    source='''
            ### Context (code) ###
            {}

            '''
    qry = get_prompt('document_readme')

    if qry is None:
        qry='''
            ### Instruction ###
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
            '''

    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = GenerativeModel(model_name)
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
        code_chat.send_message(qry)
        response = code_chat.send_message(source)

    click.echo(f"{response.text}")

@click.command(name='update-readme')
@click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_readme(context):
    """Ureate a release notes based on the context passed!
    
    
    
    
    """
    click.echo('Update README')



@click.command(name='releasenotes')
@click.option('-t', '--tag', required=False, type=str, help="The version (or tag) number for the release notes.")
# @click.option('-f', '--file', type=str, help="The existing release notes to be updated.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def releasenotes(context, tag):
    """Create a release notes based on the context passed!
    
    This is useful when no existing release notes exist. If you already have release notes `update-releasenotes` may be a better option.
    """
    
    click.echo('Generating and printing release notes.')
    version_info = f"The version number {tag} should be used." if tag else "" 
    

    source='''
            ### Context (code) ###
            {}

            '''
    qry = get_prompt('document_releasenotes') or f'''
            ### Instruction ###
            Generate comprehensive release notes for the specified software project and version. The release notes should adhere to industry best practices, be suitable for both technical users and non-technical stakeholders, and accurately reflect the changes and improvements introduced in this release.

            {version_info}

            ### Output Format ### 
            A well-structured release notes document (in Markdown format by default) that includes the following sections:

            Project Name, Version Number, Introduction (Optional): Briefly summarize the key highlights of the release.
            
            Also include Changes: Organized by categories (New Features, Enhancements, Bug Fixes, Deprecations, Other Changes), Known Issues (Optional), Additional Information (Optional)
            Ensure the release notes are clear, concise, and easy to understand for both technical and non-technical audiences.
            Use appropriate formatting (e.g., headings, lists, code blocks) for readability.
            Accurately reflect the changes and improvements made in the release.
            Are professionally written and convey the value of the new version effectively.

            ### Example Dialogue ###
            Project Name: CodeGuard Pro
            Version Number: 2.5.0
            Changes:
            * New Features:
                * Integrated code linting with customizable rule sets
                * Added support for real-time collaboration in code editing
            * Enhancements:
                * Improved code completion suggestions based on project context
                * Faster code analysis and error detection
            * Bug Fixes:
                * Resolved issue with incorrect syntax highlighting in certain languages
                * Fixed bug causing crashes when working with large files
            * Deprecations:
                * Support for Python 2.x has been removed
            * Other Changes:
                * Updated user interface for better navigation and visual appeal
            Known Issues:
            * Real-time collaboration may experience delays in slow network environments.
            '''

   
    source=source.format(format_files_as_string(context))
    
    code_chat_model = GenerativeModel(model_name)
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
        code_chat.send_message(qry)
        response = code_chat.send_message(source)

    click.echo(f"{response.text}")


@click.command(name='update-releasenotes')
@click.option('-t', '--tag', required=False, type=str, help="The version number for the release notes.")
@click.option('-f', '--file', required=True, type=str, help="The existing release notes to be updated or reviewed.")
@click.option('-c', '--context', required=False, type=str, default="", help="The code, or context, that you would like to pass.")
def update_releasenotes(context, tag, file):
    """Update release notes based on the context passed!
    
    """
    click.echo('Reviewing and updating release notes ....')

    version_info = f"The version number {tag} should be used." if tag else "" 
    
    # open the file passed and add to variable called current
    try:
        with open(file, 'r') as f:
            current = f.read()
            # click.echo(f"Current release notes: {current}")
    except FileNotFoundError:
        click.echo(f"Error: Release Notes file provided not found: {file}")
        return
    

    source='''
            ### Context (code) ###
            
            CURRENT RELEASE NOTES: 
            {current}
            
            NEW CODE:
            {context}

            '''
    qry = get_prompt('document_update_releasenotes') or f'''
            ### Instruction ###
            Review the CURRENT release notes and ensure they are comprehensive for the specified software project and version. The release notes should adhere to industry best practices, be suitable for both technical users and non-technical stakeholders.

            Should be a two part output. Part 1 discussion of the existing release notes. 
            
            Part 2 should update the release notes incorporating the discussion points and and any changes to the code accurately reflect the changes and improvements introduced in this release.

            {version_info}

            ### Output Format ### 
            Split into two parts. 

            Part 1: Discussion

            Seperate the sections with a line of -------------- FEEDBACK ^^ -------- NEW VERSION vv -----------. Part 1 should be above this line and part 2 should be below this line.
            
            The updated version sould be well-structured release notes document (in Markdown format by default) that updates the CURRENT version, incorporateing the discussion findings in part 1.
            Ensure the release notes are clear, concise, and easy to understand for both technical and non-technical audiences.
            Use appropriate formatting (e.g., headings, lists, code blocks) for readability.
            Accurately reflect the changes and improvements made in the release.
            Are professionally written and convey the value of the new version effectively.

            ### Example Dialogue ###
            ## Release Notes Review:

            **Good:**

            * The release notes clearly state the version number and project name.
            * They provide a brief overview of the release's highlights in the introduction.
            * The changes are categorized appropriately (New Features, Enhancements, Bug Fixes, Other Changes). 
            * The document mentions known issues, even if there are none.

            **Bad/Unclear:**

            * **Technical Detail:** The release notes lack specific technical details about the new caching mechanism. Providing more context, like the type of caching used (e.g., in-memory, distributed) or any configuration options available, would be helpful for technically-savvy users.
            * **User Impact:**  While the introduction mentions performance enhancements, it would be beneficial to quantify these improvements.  For example, state an estimated percentage reduction in balance retrieval times or mention the impact on database load. This makes the value proposition clearer for all audiences.
            * **Code References:** Linking the release notes to specific commits or pull requests that implement the changes would be helpful for developers who want to delve deeper into the codebase modifications.   

                        -------------- FEEDBACK ^^ -------- NEW VERSION vv -----------
            ## Updated Release Notes:

            ## Balance Reader Service - Version coffee-1.2.3

            This release introduces a new in-memory caching mechanism to significantly enhance the performance of balance retrieval, reducing the load on the backend database and speeding up balance retrieval times. Additional improvements have been made to logging and monitoring for better clarity and system insights.

            ### Changes

            **New Features:**

            * **In-Memory Caching:** To improve performance and reduce database load, we've implemented an in-memory cache for storing and retrieving account balances. This change is expected to reduce balance retrieval times significantly, especially under high load. (See code changes: [link to commit/PR]) 

            **Enhancements:**

            * **Improved Logging:** Logging messages have been refined to provide more detailed information, making it easier to troubleshoot issues and understand system behavior. (See code changes: [link to commit/PR])
            * **Enhanced Monitoring:**  Integration with Stackdriver metrics provides more comprehensive monitoring of the new caching layer and overall application performance. This enhancement enables better visibility into the service's health and performance. (See code changes: [link to commit/PR])

            **Bug Fixes:**

            * **Addressed Potential Race Condition:**  A potential race condition that could occur during concurrent transaction processing has been identified and resolved, ensuring data integrity and system stability. (See code changes: [link to commit/PR])

            **Other Changes:**

            * Updated documentation to provide guidance on the new caching mechanism and its implications for users and developers. 

            **Known Issues:**

            *  None known at this time. 
            '''

   
    source=source.format(current=current, context=format_files_as_string(context))
    
    code_chat_model = GenerativeModel(model_name)
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
        code_chat.send_message(qry)
        response = code_chat.send_message(source)

    click.echo(f"{response.text}")



@click.group()
def document():
    """
    Generate documentation for your project usnig GenAI.
    """
    pass

document.add_command(readme)
document.add_command(update_readme)
document.add_command(releasenotes)
document.add_command(update_releasenotes)
