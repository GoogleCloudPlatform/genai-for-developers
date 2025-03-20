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
        "JIRA_CLOUD": "true"  # Add JIRA_CLOUD environment variable
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
    with patch('devai.commands.jira.JIRA') as mock:
        mock_instance = MagicMock()
        mock_instance.create_issue = MagicMock(return_value=MagicMock(key="TEST-1"))
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_jira_api_wrapper():
    """Fixture to mock JiraAPIWrapper"""
    with patch('devai.commands.jira.JiraAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_agent():
    """Fixture to mock LangChain agent"""
    with patch('devai.commands.jira.initialize_agent') as mock:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(return_value="Agent response")
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_create_issue_success(mock_env_vars, mock_jira):
    """Test successful issue creation"""
    result = create_issue("Test description")
    
    assert "New issue created with key: TEST-1" in result
    mock_jira.create_issue.assert_called_once()
    call_args = mock_jira.create_issue.call_args[1]['fields']
    assert call_args['project']['key'] == "TEST"
    assert "Task" in call_args['issuetype']['name']
    assert "Test description" in call_args['description']

def test_create_command_success(cli_runner, mock_env_vars, mock_agent):
    """Test successful create command"""
    result = cli_runner.invoke(jira, ['create', '--context', 'Test issue'])
    
    assert result.exit_code == 0
    mock_agent.assert_called_once()

def test_list_command_success(cli_runner, mock_env_vars, mock_jira_api_wrapper, mock_agent):
    """Test successful list command"""
    result = cli_runner.invoke(jira, ['list', '--context', 'Test project'])
    
    assert result.exit_code == 0
    mock_agent.assert_called_once()

def test_fix_command_success(cli_runner, mock_env_vars, mock_llm, mock_agent):
    """Test successful fix command"""
    result = cli_runner.invoke(jira, ['fix', '--context', 'Test fix'])
    
    assert result.exit_code == 0
    mock_llm.invoke.assert_called_once()
    mock_agent.assert_called_once()

def test_missing_env_vars(cli_runner):
    """Test error handling for missing environment variables"""
    with patch.dict(os.environ, {}, clear=True):
        result = cli_runner.invoke(jira, ['create', '--context', 'Test'])
        
        assert result.exit_code == 1
        assert "PROJECT_ID" in result.output
        assert "JIRA_USERNAME" in result.output
        assert "JIRA_API_TOKEN" in result.output
        assert "JIRA_INSTANCE_URL" in result.output
        assert "JIRA_PROJECT_KEY" in result.output

def test_jira_api_error(cli_runner, mock_env_vars, mock_jira):
    """Test error handling for JIRA API errors"""
    mock_jira.create_issue.side_effect = Exception("JIRA API Error")
    
    with pytest.raises(click.ClickException, match="JIRA API Error"):
        create_issue("Test description") 