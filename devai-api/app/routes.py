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

import os
from typing import Any, Mapping, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi import APIRouter, Body, FastAPI, HTTPException, Request


from google.auth.transport import requests  # type:ignore
from google.oauth2 import id_token  # type:ignore
from langchain.embeddings.base import Embeddings

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
from langchain_google_vertexai import ChatVertexAI
from google.cloud.aiplatform import telemetry
from vertexai.generative_models import GenerativeModel
import sys
sys.path.append('../package') 
from secret_manager import get_access_secret

USER_AGENT = 'cloud-solutions/genai-for-developers-v1.0'

INSTRUCTION_ID='generate_handler_instruction'
model_name="gemini-1.5-pro-preview-0409"

with telemetry.tool_context_manager(USER_AGENT):
    llm = ChatVertexAI(model_name=model_name,
        convert_system_message_to_human=True,
        temperature=0.2,
        max_output_tokens=4096)

gitlab = GitLabAPIWrapper()
toolkit = GitLabToolkit.from_gitlab_api_wrapper(gitlab)

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

routes = APIRouter()
code_chat_model = GenerativeModel(model_name)

@routes.get("/")
async def root():
    """Index endpoint"""
    return {"message": "DevAI API"}

@routes.get("/test")
async def test():
    """Test endpoint"""
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
    response = code_chat.send_message("Tell me about Google Gemini 1.5 capabilities")
    print(f"Response from Model:\n{response.text}\n")
    return {"message": response.text}

@routes.post("/generate", response_class=PlainTextResponse)
async def generate_handler(request: Request, prompt: str = Body(embed=True)):
    """Handler for Generate Content Requests"""
    # Retrieve user prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Error: Prompt is required")

    instructions = get_access_secret( INSTRUCTION_ID)
    
    if instructions is None:
        instructions = f"""You are principal software engineer at Google and given requirements below for implementation.
        Please provide implementation details and document the implementation.
    
        REQUIREMENTS:
        {prompt}
        """
    with telemetry.tool_context_manager(USER_AGENT):
        code_chat = code_chat_model.start_chat()
    response = code_chat.send_message(instructions)
    print(f"Response from Model:\n{response.text}\n")

    # resp_text = response.candidates[0].content.parts[0].text

    # pr_prompt = f"""Create GitLab merge request using provided details below.
    # Create new files, commit them and push them to opened merge request.
    # When creating new files, remove the lines that start with ``` before saving the files.

    # DETAILS: 
    # {resp_text}
    # """

    # print(pr_prompt)
    # agent.invoke(pr_prompt)

    return response.text

