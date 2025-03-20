import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from devai.commands.release import (
    release, check_git_environment, check_if_string_is_in_list,
    get_model, summary_for_tag, report, notes
)
import subprocess
from devai.util.constants import GEMINI_PRO_MODEL

@pytest.fixture
def mock_generative_model():
    """Fixture to mock Vertex AI GenerativeModel"""
    with patch('devai.commands.release.GenerativeModel') as mock:
        mock_instance = MagicMock()
        mock_instance.generate_content = MagicMock(return_value=MagicMock(text="Test response"))
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_file_processor():
    """Fixture to mock file processor functions"""
    with patch('devai.commands.release.format_files_as_string') as mock_format, \
         patch('devai.commands.release.list_files') as mock_list_files, \
         patch('devai.commands.release.list_changes') as mock_list_changes, \
         patch('devai.commands.release.list_commit_messages') as mock_list_messages, \
         patch('devai.commands.release.list_commits_for_branches') as mock_list_branches, \
         patch('devai.commands.release.list_tags') as mock_list_tags, \
         patch('devai.commands.release.list_commits_for_tags') as mock_list_tag_commits:
        
        mock_format.return_value = "test code content"
        mock_list_files.return_value = ["file1.py", "file2.py"]
        mock_list_changes.return_value = "test changes"
        mock_list_messages.return_value = "test commit messages"
        mock_list_branches.return_value = ["commit1", "commit2"]
        mock_list_tags.return_value = ["v1.0.0", "v1.1.0"]
        mock_list_tag_commits.return_value = ["commit1", "commit2"]
        
        yield {
            'format': mock_format,
            'list_files': mock_list_files,
            'list_changes': mock_list_changes,
            'list_messages': mock_list_messages,
            'list_branches': mock_list_branches,
            'list_tags': mock_list_tags,
            'list_tag_commits': mock_list_tag_commits
        }

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_check_git_environment_success():
    """Test successful git environment check"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        is_valid, error_msg = check_git_environment()
        assert is_valid
        assert error_msg == ""
        assert mock_run.call_count == 3

def test_check_git_environment_not_git_repo():
    """Test git environment check with not a git repo"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git', stderr=b'not a git repository')
        is_valid, error_msg = check_git_environment()
        assert not is_valid
        assert "Not a git repository" in error_msg

def test_check_git_environment_no_user_config():
    """Test git environment check with missing user config"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git', stderr=b'user.name not set')
        is_valid, error_msg = check_git_environment()
        assert not is_valid
        assert "Git user configuration missing" in error_msg

def test_check_if_string_is_in_list():
    """Test string list membership check"""
    test_list = ["item1", "item2", "item3"]
    assert check_if_string_is_in_list("item1", test_list)
    assert not check_if_string_is_in_list("item4", test_list)

def test_get_model():
    """Test model initialization"""
    with patch('devai.commands.release.GenerativeModel') as mock:
        model = get_model()
        mock.assert_called_once_with(GEMINI_PRO_MODEL)
        mock.assert_called_once_with("gemini-pro")
        assert model == mock.return_value

def test_summary_for_tag_success(mock_generative_model, mock_file_processor):
    """Test successful summary generation"""
    result = summary_for_tag("v1.1.0", "test query")
    
    assert result == "Test response"
    mock_generative_model.generate_content.assert_called_once()
    mock_file_processor['list_tags'].assert_called_once()
    mock_file_processor['list_changes'].assert_called_once()
    mock_file_processor['list_messages'].assert_called_once()
    mock_file_processor['format'].assert_called_once()

def test_summary_for_tag_no_tags(mock_file_processor):
    """Test summary generation with no tags"""
    mock_file_processor['list_tags'].return_value = []
    
    with pytest.raises(SystemExit):
        summary_for_tag("v1.1.0", "test query")

def test_summary_for_tag_invalid_tag(mock_file_processor):
    """Test summary generation with invalid tag"""
    mock_file_processor['list_tags'].return_value = ["v1.0.0"]
    
    with pytest.raises(SystemExit):
        summary_for_tag("v1.1.0", "test query")

def test_summary_for_tag_single_tag(mock_generative_model, mock_file_processor):
    """Test summary generation with single tag"""
    mock_file_processor['list_tags'].return_value = ["v1.0.0"]
    result = summary_for_tag("v1.0.0", "test query")
    
    assert result == "Test response"
    mock_file_processor['list_tag_commits'].assert_called_once_with("v1.0.0", "HEAD")

def test_report_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful report command execution"""
    with patch('devai.commands.release.check_git_environment', return_value=(True, "")):
        result = cli_runner.invoke(report, ['-t', 'v1.1.0'])
        
        assert result.exit_code == 0
        assert "report" in result.output
        assert "tag=v1.1.0" in result.output
        assert "Test response" in result.output

def test_report_command_git_error(cli_runner):
    """Test report command with git environment error"""
    with patch('devai.commands.release.check_git_environment', return_value=(False, "Git error")):
        result = cli_runner.invoke(report, ['-t', 'v1.1.0'])
        
        assert result.exit_code == 1
        assert "Error: Git error" in result.output

def test_notes_command_success(cli_runner, mock_generative_model, mock_file_processor):
    """Test successful notes command execution"""
    with patch('devai.commands.release.check_git_environment', return_value=(True, "")):
        result = cli_runner.invoke(notes, ['-t', 'v1.1.0'])
        
        assert result.exit_code == 0
        assert "notes" in result.output
        assert "tag=v1.1.0" in result.output
        assert "Test response" in result.output

def test_notes_command_git_error(cli_runner):
    """Test notes command with git environment error"""
    with patch('devai.commands.release.check_git_environment', return_value=(False, "Git error")):
        result = cli_runner.invoke(notes, ['-t', 'v1.1.0'])
        
        assert result.exit_code == 1
        assert "Error: Git error" in result.output

def test_release_group():
    """Test release command group structure"""
    assert release.name == 'release'
    assert 'report' in release.commands
    assert 'notes_user_tag' in release.commands 