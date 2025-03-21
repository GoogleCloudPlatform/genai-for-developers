import pytest
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from devai.commands.document import (
    document, ensure_env_variable, get_prompt,
    readme, update_readme, releasenotes, update_releasenotes
)
from google.api_core.exceptions import NotFound, PermissionDenied
import os

@pytest.fixture
def mock_generative_model():
    """Fixture to mock Vertex AI GenerativeModel"""
    with patch('devai.commands.document.GenerativeModel') as mock:
        mock_instance = MagicMock()
        mock_chat = MagicMock()
        mock_chat.send_message = MagicMock(return_value=MagicMock(text="Test response"))
        mock_instance.start_chat = MagicMock(return_value=mock_chat)
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_secret_manager():
    """Fixture to mock Secret Manager client"""
    with patch('devai.commands.document.secretmanager.SecretManagerServiceClient') as mock:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "Test prompt"
        mock_instance.access_secret_version = MagicMock(return_value=mock_response)
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_file_processor():
    """Fixture to mock file processor"""
    with patch('devai.commands.document.format_files_as_string') as mock:
        mock.return_value = "test code content"
        yield mock

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_ensure_env_variable_success():
    """Test successful environment variable check"""
    with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
        value = ensure_env_variable('TEST_VAR')
        assert value == 'test_value'

def test_ensure_env_variable_missing():
    """Test missing environment variable"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError) as exc:
            ensure_env_variable('TEST_VAR')
        assert "Required environment variable 'TEST_VAR' is not set" in str(exc.value)

def test_get_prompt_success(mock_secret_manager):
    """Test successful prompt retrieval"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        result = get_prompt('test-secret')
        
        assert result == "Test prompt"
        mock_secret_manager.access_secret_version.assert_called_once()

def test_get_prompt_missing_project_id():
    """Test prompt retrieval with missing PROJECT_ID"""
    with patch.dict(os.environ, {}, clear=True):
        result = get_prompt('test-secret')
        assert result is None

def test_get_prompt_permission_denied(mock_secret_manager):
    """Test prompt retrieval with permission denied"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        mock_secret_manager.access_secret_version.side_effect = PermissionDenied('test')
        result = get_prompt('test-secret')
        assert result is None

def test_get_prompt_not_found(mock_secret_manager):
    """Test prompt retrieval with secret not found"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        mock_secret_manager.access_secret_version.side_effect = NotFound('test')
        result = get_prompt('test-secret')
        assert result is None

def test_get_prompt_unexpected_error(mock_secret_manager):
    """Test prompt retrieval with an unexpected error"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        mock_secret_manager.access_secret_version.side_effect = Exception('Unexpected error')
        result = get_prompt('test-secret')
        assert result is None

def test_readme_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful readme generation"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        result = cli_runner.invoke(document, ['readme', '--context', 'test code'])
        
        assert result.exit_code == 0
        assert "Generating and printing the README" in result.output
        assert "Test response" in result.output
        mock_file_processor.assert_called_once_with('test code')

def test_readme_command_with_file_and_branch(cli_runner, mock_generative_model, mock_file_processor):
    """Test readme generation with file and branch options"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        result = cli_runner.invoke(document, [
            'readme',
            '--context', 'test code',
            '--file', 'README.md',
            '--branch', 'feature/readme'
        ])
        
        assert result.exit_code == 0
        assert "Generating and printing the README" in result.output

def test_update_readme_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful readme update"""
    test_content = "# Existing README"
    with patch('builtins.open', mock_open(read_data=test_content)):
        result = cli_runner.invoke(document, [
            'update-readme',
            '--file', 'README.md',
            '--context', 'test code'
        ])
        
        assert result.exit_code == 0
        assert "Reviewing and updating README" in result.output
        assert "Test response" in result.output

def test_update_readme_command_file_not_found(cli_runner):
    """Test readme update with missing file"""
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = cli_runner.invoke(document, [
            'update-readme',
            '--file', 'nonexistent.md',
            '--context', 'test code'
        ])
        
        assert result.exit_code == 0  # Click returns 0 for handled errors
        assert "Error: Release Notes file provided not found" in result.output

def test_releasenotes_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful release notes generation"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        result = cli_runner.invoke(document, [
            'releasenotes',
            '--context', 'test code',
            '--tag', 'v1.0.0'
        ])
        
        assert result.exit_code == 0
        assert "Test response" in result.output

def test_update_releasenotes_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful release notes update"""
    test_content = "# Existing Release Notes"
    with patch('builtins.open', mock_open(read_data=test_content)):
        result = cli_runner.invoke(document, [
            'update-releasenotes',
            '--file', 'RELEASE.md',
            '--context', 'test code',
            '--tag', 'v1.0.0'
        ])
        
        assert result.exit_code == 0
        assert "Test response" in result.output

def test_update_releasenotes_command_file_not_found(cli_runner):
    """Test release notes update with missing file"""
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = cli_runner.invoke(document, [
            'update-releasenotes',
            '--file', 'nonexistent.md',
            '--context', 'test code',
            '--tag', 'v1.0.0'
        ])
        
        assert result.exit_code == 0  # Click returns 0 for handled errors
        assert "Error: Release Notes file provided not found" in result.output

def test_readme_command_llm_failure(cli_runner, mock_generative_model, mock_file_processor):
    """Test readme generation with LLM failure"""
    with patch.dict(os.environ, {'PROJECT_ID': 'test-project'}):
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = Exception('LLM error')
        mock_generative_model.start_chat.return_value = mock_chat
        
        result = cli_runner.invoke(document, ['readme', '--context', 'test code'])
        
        assert result.exit_code == 0
        assert "Failed to call LLM: LLM error" in result.output

def test_document_group():
    """Test document command group structure"""
    assert document.name == 'document'
    assert 'readme' in document.commands
    assert 'update-readme' in document.commands
    assert 'releasenotes' in document.commands
    assert 'update-releasenotes' in document.commands 