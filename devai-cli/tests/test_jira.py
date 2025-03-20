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
def mock_git():
    """Fixture to mock git operations"""
    with patch('os.system') as mock:
        def side_effect(cmd):
            if cmd == "git checkout -b fix/test-1":
                return 0
            elif cmd == "git add .":
                return 0
            elif cmd == 'git commit -m "Fix TEST-1: Test fix"':
                return 0
            return 1
        mock.side_effect = side_effect
        yield mock

@pytest.fixture
def mock_jira_toolkit():
    """Fixture to mock JiraToolkit"""
    with patch('langchain_community.agent_toolkits.jira.toolkit.JiraToolkit') as mock:
        mock_instance = MagicMock()
        mock_instance.get_tools = MagicMock(return_value=[])
        mock.return_value = mock_instance
        yield mock_instance

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

def test_fix_command_success(cli_runner, mock_env_vars, mock_telemetry, mock_chat_vertex, mock_path, mock_git, mock_jira, mock_jira_api_wrapper, mock_jira_toolkit, mock_agent):
    """Test successful fix command"""
    # Mock file changes
    mock_file_changes = [
        {
            'path': 'test.py',
            'content': 'def test_function():\n    return "test"'
        }
    ]

    with patch('devai.commands.jira.get_issue_details', return_value={
        'key': 'TEST-1',
        'summary': 'Test fix',
        'description': 'Test description',
        'status': 'Open'
    }), \
         patch('devai.commands.jira.parse_file_changes', return_value=mock_file_changes), \
         patch('devai.commands.utils.get_llm', return_value=mock_chat_vertex), \
         patch('langchain_community.utilities.jira.JiraAPIWrapper', return_value=mock_jira_api_wrapper), \
         patch('langchain_community.agent_toolkits.jira.toolkit.JiraToolkit.from_jira_api_wrapper', return_value=mock_jira_toolkit), \
         patch('langchain.agents.initialize_agent', return_value=mock_agent), \
         patch('jira.JIRA', return_value=mock_jira):

        result = cli_runner.invoke(jira, ['fix', '--context', 'TEST-1'])

        print(f"Result output: {result.output}")
        print(f"Result exception: {result.exception}")

        assert result.exit_code == 0
        mock_chat_vertex.invoke.assert_called_once()
        mock_agent.run.assert_not_called()
        mock_git.assert_any_call("git checkout -b fix/test-1")
        mock_git.assert_any_call("git add .")
        mock_git.assert_any_call('git commit -m "Fix TEST-1: Test fix"')
        mock_path.write_text.assert_called_once_with('def test_function():\n    return "test"')

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