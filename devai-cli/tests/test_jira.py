import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from devai.commands.jira import jira, create_issue
import os
import click

@pytest.fixture
def mock_env_vars():
    """Fixture to set required environment variables"""
    env_vars = {
        "PROJECT_ID": "test-project",
        "LOCATION": "us-central1",
        "JIRA_USERNAME": "test-user",
        "JIRA_API_TOKEN": "test-token",
        "JIRA_INSTANCE_URL": "https://test.atlassian.net",
        "JIRA_PROJECT_KEY": "TEST",
        "JIRA_CLOUD": "true",
        "GOOGLE_CLOUD_PROJECT": "test-project"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_llm():
    """Fixture to mock Vertex AI ChatVertexAI"""
    with patch('devai.commands.jira.ChatVertexAI') as mock:
        mock_instance = MagicMock()
        mock_instance.invoke = MagicMock(return_value=MagicMock(content="Test response"))
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_jira():
    """Fixture to mock JIRA client"""
    with patch('jira.JIRA') as mock:
        mock_instance = MagicMock()
        mock_instance.issue = MagicMock(return_value=MagicMock(
            key='TEST-1',
            fields=MagicMock(
                summary='Test fix',
                description='Test description',
                status=MagicMock(name='Open')
            )
        ))
        mock_instance.transitions = MagicMock(return_value=[{'id': '1', 'name': 'Done'}])
        mock_instance.transition_issue = MagicMock()
        mock_instance.add_comment = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_jira_api_wrapper():
    """Fixture to mock JiraAPIWrapper"""
    with patch('langchain_community.utilities.jira.JiraAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock_instance.issue = MagicMock(return_value={
            'key': 'TEST-1',
            'summary': 'Test fix',
            'description': 'Test description',
            'status': 'Open'
        })
        mock_instance.transitions = MagicMock(return_value=[{'id': '1', 'name': 'Done'}])
        mock_instance.transition_issue = MagicMock()
        mock_instance.add_comment = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_agent():
    """Fixture to mock LangChain agent"""
    with patch('langchain.agents.initialize_agent') as mock:
        mock_instance = MagicMock()
        mock_instance.run = MagicMock(return_value="Test response")
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

@pytest.fixture
def mock_telemetry():
    """Fixture to mock telemetry context manager"""
    with patch('google.cloud.aiplatform.telemetry.tool_context_manager') as mock:
        mock.return_value.__enter__ = MagicMock()
        mock.return_value.__exit__ = MagicMock()
        yield mock

@pytest.fixture
def mock_chat_vertex():
    """Fixture to mock ChatVertexAI"""
    with patch('langchain_google_vertexai.ChatVertexAI') as mock:
        mock_instance = MagicMock()
        mock_instance.invoke = MagicMock(return_value=MagicMock(content="""
        test.py
        ```
        def test_function():
            return "test"
        ```
        """))
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_path():
    """Fixture to mock Path operations"""
    with patch('pathlib.Path') as mock:
        mock_instance = MagicMock()
        mock_instance.parent = MagicMock()
        mock_instance.write_text = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_jira_toolkit():
    """Fixture to mock JiraToolkit"""
    with patch('langchain_community.agent_toolkits.jira.toolkit.JiraToolkit') as mock:
        mock_instance = MagicMock()
        mock_instance.get_tools = MagicMock(return_value=[])
        mock.return_value = mock_instance
        yield mock_instance






