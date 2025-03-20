import pytest
from unittest.mock import patch, MagicMock
from click import ClickException
from devai.commands.github_cmd import generate_pr_summary, create_github_pr

@pytest.fixture
def mock_vertex_ai():
    """Fixture to mock ChatVertexAI initialization"""
    with patch('devai.commands.github_cmd.ChatVertexAI') as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test PR\nThis is a test PR."
        mock_model.invoke = MagicMock(return_value=mock_response)
        mock.return_value = mock_model
        yield mock

@pytest.fixture
def mock_github_api():
    """Fixture to mock GitHubAPIWrapper initialization"""
    with patch('devai.commands.github_cmd.GitHubAPIWrapper') as mock:
        mock_github = MagicMock()
        mock_github.create_branch = MagicMock(return_value="Branch created")
        mock_github.read_file = MagicMock(return_value="old content")
        mock_github.update_file = MagicMock(return_value="File updated")
        mock_github.create_pull_request = MagicMock(return_value="PR created")
        mock.return_value = mock_github
        yield mock_github

@pytest.fixture
def mock_env_vars():
    """Fixture to mock required environment variables"""
    with patch.dict('os.environ', {
        'PROJECT_ID': 'test-project',
        'LOCATION': 'test-location',
        'GITHUB_APP_ID': 'test-app-id',
        'GITHUB_APP_PRIVATE_KEY': 'test-private-key',
        'GITHUB_REPOSITORY': 'test-repo'
    }):
        yield

def test_generate_pr_summary(mock_vertex_ai, mock_env_vars, mock_github_api):
    """Test generating a PR summary"""
    old_code = "def old():\n    pass"
    new_code = "def new():\n    return True"
    
    result = generate_pr_summary(old_code, new_code)
    
    assert result == "Test PR\nThis is a test PR."
    mock_vertex_ai.return_value.invoke.assert_called_once()

def test_create_github_pr(mock_github_api, mock_vertex_ai, mock_env_vars):
    """Test creating a GitHub PR"""
    branch = "test-branch"
    files = {
        "test.py": "def test():\n    return True"
    }
    
    create_github_pr(branch, files)
    
    mock_github_api.create_branch.assert_called_once_with(branch)
    mock_github_api.read_file.assert_called_once_with("test.py")
    mock_github_api.update_file.assert_called_once()
    mock_github_api.create_pull_request.assert_called_once()

def test_error_handling_missing_env_vars():
    """Test error handling when environment variables are missing"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ClickException) as exc_info:
            generate_pr_summary("old", "new")
        assert "Missing required environment variables: PROJECT_ID" in str(exc_info.value)

def test_error_handling_github_api_failure(mock_github_api, mock_vertex_ai, mock_env_vars):
    """Test error handling when GitHub API calls fail"""
    mock_github_api.create_branch.side_effect = Exception("API Error")
    
    create_github_pr("test-branch", {"test.py": "test"})
    
    mock_github_api.create_branch.assert_called_once()
    mock_github_api.read_file.assert_not_called()
    mock_github_api.update_file.assert_not_called()
    mock_github_api.create_pull_request.assert_not_called() 