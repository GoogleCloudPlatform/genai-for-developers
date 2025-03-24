import os
import click
from google.cloud.aiplatform import telemetry
from langchain_google_vertexai import ChatVertexAI

from .constants import USER_AGENT, MODEL_NAME

def check_required_env_vars():
    """Check for required environment variables"""
    required_vars = [
        "PROJECT_ID",
        "LOCATION",
        "JIRA_USERNAME",
        "JIRA_API_TOKEN",
        "JIRA_INSTANCE_URL",
        "JIRA_PROJECT_KEY"
    ]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise click.ClickException(f"Missing required environment variables: {', '.join(missing_vars)}")

def get_llm():
    """Get Vertex AI ChatVertexAI instance"""
    check_required_env_vars()
    with telemetry.tool_context_manager(USER_AGENT):
        return ChatVertexAI(
            model_name=MODEL_NAME,
            project=os.environ["PROJECT_ID"],
            location=os.environ["LOCATION"],
            max_output_tokens=1024,
            temperature=0.1
        ) 