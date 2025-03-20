# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import APIRouter, Body, HTTPException, Request


from google.cloud.aiplatform import telemetry
from vertexai.generative_models import GenerativeModel

from .jira import create_jira_issue
from .github_utils import create_pull_request
from .gitlab_utils import create_merge_request, MergeRequestError
from .api_utils import validate_api_key
from .constants import USER_AGENT, MODEL_NAME

routes = APIRouter()
code_chat_model = GenerativeModel(MODEL_NAME)

@routes.get("/")
async def root():
    """Index endpoint"""
    return {"message": "DevAI API"}

@routes.get("/test")
async def test(request: Request):
    # Validate API key
    if not validate_api_key(request.headers.get('x-devai-api-key')):
        raise HTTPException(status_code=401, detail="Error: Unauthorized")
    """Test endpoint"""
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat(response_validation=False)
        response = code_chat.send_message("Describe Developer Productivity with GenAI")
    print(f"Response from Model:\n{response.text}\n")
    return {"message": response.text}


@routes.post("/create-github-pr", response_class=PlainTextResponse)
async def generate_handler(request: Request, prompt: str = Body(embed=True)):
    """Handler for GitHub Pull Requests Generation"""
    # Validate API key
    if not validate_api_key(request.headers.get('x-devai-api-key')):
        raise HTTPException(status_code=401, detail="Error: Unauthorized")
    # Retrieve user prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Error: Prompt is required")

    pr_details = create_pull_request(prompt)

    return pr_details

@routes.post("/create-gitlab-mr", response_class=PlainTextResponse)
async def generate_handler(request: Request, prompt: str = Body(embed=True)):
    """Handler for GitLab Merge Requests Generation"""
    # Validate API key
    if not validate_api_key(request.headers.get('x-devai-api-key')):
        raise HTTPException(status_code=401, detail="Error: Unauthorized")
    # Retrieve user prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Error: Prompt is required")

    try:
        return create_merge_request(prompt)
    except MergeRequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create merge request: {e}") from e
    

@routes.post("/generate", response_class=PlainTextResponse)
async def generate_handler(request: Request, prompt: str = Body(embed=True)):
    """Handler for GitLab Merge Requests Generation"""
    # Validate API key
    if not validate_api_key(request.headers.get('x-devai-api-key')):
        raise HTTPException(status_code=401, detail="Error: Unauthorized")
    # Retrieve user prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Error: Prompt is required")

    try:
        return create_merge_request(prompt)
    except MergeRequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create merge request: {e}") from e
    

@routes.post("/create-jira-issue", response_class=JSONResponse)
async def create_jira_issue_handler(request: Request, prompt: str = Body(embed=True)):
    """Handler for JIRA Issue Creation Content Requests"""
    # Retrieve user prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Error: Prompt is required")

    instructions = f"""You are a senior staff software engineer at Google and will be given REQUIREMENTS below.
    Write a very detailed technical description for JIRA user story based on input requirements. 
    
    EXAMPLE:
    create a url shortener in python using FASTAPI framework. Output must include python source code, unit tests, documentation.
    
    OUTPUT:
    Create a URL Shortener Microservice using FastAPI
    As a developer, I want to create a URL shortener microservice using FastAPI to shorten long URLs and retrieve the original URLs from short codes.
    Acceptance Criteria:
    Functionality:
    The service must accept a long URL as input and generate a short code.
    The service must be able to retrieve the original URL based on the short code.
    The short codes should be unique and randomly generated.
    The service should provide a simple API for both shortening and retrieving URLs.
    Implementation:
    The microservice should be built using FastAPI framework.
    The service should store the URL mappings in a database. (Choose a suitable database based on your needs)
    The code should be well-documented and follow best practices.
    The service should include unit tests for all core functionalities.
    Documentation:
    Create a comprehensive documentation with API specifications, usage instructions, and deployment details.
    The documentation should be accessible through a README file.
    Code Structure:
    The code should be organized into separate modules for different functionalities.
    The source code should be properly formatted and adhere to PEP 8 style guide.
    Output:
    Python Source Code: Provide the complete Python code for the URL shortener microservice.
    Unit Tests: Include a comprehensive set of unit tests covering all core functionalities.
    Documentation: Create a detailed README file containing API specifications, usage instructions, deployment guide, and any other relevant information.
    
    REQUIREMENTS:
    {prompt}
    """
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat(response_validation=False)
        response = code_chat.send_message(instructions)

        create_jira_issue("New JIRA Issue", response.text)

    return {"message": "JIRA issue was created: https://cymbal-eats.atlassian.net/jira/software/projects/CYMEATS/boards/1"}
