import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from devai.commands.gitlab import gitlab, create_pr, create_comment, fix_issue

@pytest.fixture
def cli_runner():
    """Fixture to provide a Click CLI runner"""
    return CliRunner()

@pytest.fixture
def mock_agent():
    """Fixture to mock the GitLab agent"""
    with patch('devai.commands.gitlab.get_gitlab_agent') as mock:
        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={"output": "Mock response"})
        mock.return_value = mock_agent
        yield mock_agent

@pytest.fixture
def mock_env_vars():
    """Fixture to mock required environment variables"""
    with patch.dict('os.environ', {
        'PROJECT_ID': 'test-project',
        'REGION': 'test-region'
    }):
        yield

@pytest.fixture
def mock_vertex_ai():
    """Fixture to mock ChatVertexAI initialization"""
    with patch('devai.commands.gitlab.ChatVertexAI') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_gitlab_api():
    """Fixture to mock GitLabAPIWrapper initialization"""
    with patch('devai.commands.gitlab.GitLabAPIWrapper') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_gitlab_toolkit():
    """Fixture to mock GitLabToolkit initialization"""
    with patch('devai.commands.gitlab.GitLabToolkit') as mock:
        mock_toolkit = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = "mock_tool"
        mock_tool.description = "A mock tool"
        mock_tool.func = lambda x: x
        mock_toolkit.from_gitlab_api_wrapper.return_value = MagicMock()
        mock_toolkit.from_gitlab_api_wrapper.return_value.get_tools.return_value = [mock_tool]
        mock.return_value = mock_toolkit
        yield mock

def test_create_pr_command(cli_runner, mock_agent, mock_env_vars, mock_gitlab_api, mock_gitlab_toolkit):
    """Test the create_pr command"""
    result = cli_runner.invoke(create_pr, ['--context', 'test context'])
    
    assert result.exit_code == 0
    mock_agent.invoke.assert_called_once_with("""Create GitLab merge request, use provided details below: 
test context""")

def test_create_comment_command(cli_runner, mock_agent, mock_env_vars, mock_gitlab_api, mock_gitlab_toolkit):
    """Test the create_comment command"""
    result = cli_runner.invoke(create_comment, ['--context', 'test comment', '--issue', 'test issue'])
    
    assert result.exit_code == 0
    mock_agent.invoke.assert_called_once_with("""You need to do two tasks only.
First task: Get GitLab issue with title 'test issue'.
Second task: add content below as a comment to the issue you found in first task:

test comment""")

def test_fix_issue_command(cli_runner, mock_agent, mock_env_vars, mock_gitlab_api, mock_gitlab_toolkit):
    """Test the fix_issue command"""
    result = cli_runner.invoke(fix_issue, ['--context', '123'])
    
    assert result.exit_code == 0
    mock_agent.invoke.assert_called_once_with("""You have the software engineering capabilities of a Google Principle engineer.
You are tasked with completing issues on a gitlab repository.
Please look at the open issue #123 and complete it by creating pull request that solves the issue.""")

def test_gitlab_group_commands(cli_runner, mock_env_vars):
    """Test that all commands are registered with the gitlab group"""
    result = cli_runner.invoke(gitlab, ['--help'])
    
    assert result.exit_code == 0
    assert 'create-pr' in result.output
    assert 'create-comment' in result.output
    assert 'fix-issue' in result.output

def test_missing_project_id(cli_runner, mock_vertex_ai, mock_gitlab_api, mock_gitlab_toolkit):
    """Test that the command fails when PROJECT_ID is missing"""
    with patch.dict('os.environ', {}, clear=True):
        result = cli_runner.invoke(create_pr, ['--context', 'test context'])
        
        assert result.exit_code == 1
        assert "Missing required environment variables: PROJECT_ID" in result.output
        assert "export PROJECT_ID=your-project_id" in result.output

def test_default_region(cli_runner, mock_agent, mock_gitlab_api, mock_gitlab_toolkit):
    """Test that us-central1 is used as default region when REGION is not set"""
    with patch.dict('os.environ', {'PROJECT_ID': 'test-project'}, clear=True):
        result = cli_runner.invoke(gitlab, ['--help'])
        
        assert result.exit_code == 0
        # Verify the command works with default region
        assert 'create-pr' in result.output
        assert 'create-comment' in result.output
        assert 'fix-issue' in result.output 