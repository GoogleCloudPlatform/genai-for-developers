import pytest
from unittest.mock import patch, mock_open, MagicMock
from devai.util.file_processor import (
    is_ascii_text, get_text_files_contents, format_files_as_string,
    list_files, list_changes, list_commit_messages, list_commits_for_branches,
    list_commits_for_tags, list_tags, run_git_command
)
import os
import subprocess

@pytest.fixture
def mock_git_output():
    """Fixture to mock git command outputs"""
    with patch('subprocess.check_output') as mock:
        mock.return_value = b'file1.py\nfile2.py\n'
        yield mock

@pytest.fixture
def mock_os_path():
    """Fixture to mock os.path functions"""
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.isdir') as mock_isdir:
        mock_exists.return_value = True
        mock_isdir.return_value = False
        yield mock_exists, mock_isdir

def test_is_ascii_text_success():
    """Test successful ASCII text check"""
    with patch('builtins.open', mock_open(read_data='test content')):
        assert is_ascii_text('test.txt')

def test_is_ascii_text_binary():
    """Test ASCII text check with binary file"""
    with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'test')):
        assert not is_ascii_text('test.bin')

def test_is_ascii_text_file_not_found():
    """Test ASCII text check with missing file"""
    with patch('builtins.open', side_effect=FileNotFoundError):
        assert not is_ascii_text('nonexistent.txt')

def test_get_text_files_contents_success():
    """Test successful file contents retrieval"""
    mock_files = {
        'dir1/file1.txt': 'content1',
        'dir1/file2.txt': 'content2',
        'dir1/dir2/file3.txt': 'content3'
    }
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('dir1', ['dir2'], ['file1.txt', 'file2.txt']),
            ('dir1/dir2', [], ['file3.txt'])
        ]
        
        with patch('builtins.open', mock_open(read_data='test content')):
            result = get_text_files_contents('test_dir')
            assert len(result) == 3
            assert all(path in result for path in mock_files.keys())

def test_get_text_files_contents_with_ignore():
    """Test file contents retrieval with ignored files"""
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('dir1', ['venv', 'dir2'], ['file1.txt', '__pycache__']),
            ('dir1/dir2', [], ['file2.txt'])
        ]
        
        with patch('builtins.open', mock_open(read_data='test content')):
            result = get_text_files_contents('test_dir', ignore=['venv', '__pycache__'])
            assert len(result) == 2
            assert 'dir1/file1.txt' in result
            assert 'dir1/dir2/file2.txt' in result

def test_format_files_as_string_directory(mock_os_path):
    """Test formatting files from directory"""
    mock_exists, mock_isdir = mock_os_path
    mock_isdir.return_value = True
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('dir1', ['dir2'], ['file1.txt', 'file2.txt']),
            ('dir1/dir2', [], ['file3.txt'])
        ]
        
        with patch('builtins.open', mock_open(read_data='test content')):
            result = format_files_as_string('test_dir')
            assert 'file: dir1/file1.txt' in result
            assert 'content:\ntest content' in result
            assert 'file: dir1/file2.txt' in result
            assert 'file: dir1/dir2/file3.txt' in result

def test_format_files_as_string_single_file(mock_os_path):
    """Test formatting single file"""
    with patch('builtins.open', mock_open(read_data='test content')):
        result = format_files_as_string('test.txt')
        assert 'file: test.txt' in result
        assert 'content:\ntest content' in result

def test_format_files_as_string_file_list(mock_os_path):
    """Test formatting list of files"""
    with patch('builtins.open', mock_open(read_data='test content')):
        result = format_files_as_string(['file1.txt', 'file2.txt'])
        assert 'file: file1.txt' in result
        assert 'content:\ntest content' in result
        assert 'file: file2.txt' in result

def test_format_files_as_string_invalid_input():
    """Test formatting with invalid input"""
    with pytest.raises(ValueError):
        format_files_as_string(123)

def test_list_files_success(mock_git_output):
    """Test successful file listing"""
    result = list_files('abc123', 'def456')
    assert result == ['file1.py', 'file2.py']
    mock_git_output.assert_called_once_with(
        ['git', 'diff', '--name-only', 'abc123', 'def456']
    )

def test_list_files_with_parent(mock_git_output):
    """Test file listing with parent commit"""
    result = list_files('abc123', 'def456', refer_commit_parent=True)
    assert result == ['file1.py', 'file2.py']
    mock_git_output.assert_called_once_with(
        ['git', 'diff', '--name-only', 'abc123^', 'def456']
    )

def test_list_changes_success(mock_git_output):
    """Test successful changes listing"""
    mock_git_output.return_value = b'diff --git a/file1.py b/file1.py\n+new line'
    result = list_changes('abc123', 'def456')
    assert 'diff --git' in result.decode('utf-8')
    assert 'new line' in result.decode('utf-8')

def test_list_commit_messages_success(mock_git_output):
    """Test successful commit messages listing"""
    mock_git_output.return_value = b'commit1\nfile1.py\ncommit2\nfile2.py'
    result = list_commit_messages('abc123', 'def456')
    assert 'commit1' in result.decode('utf-8')
    assert 'commit2' in result.decode('utf-8')

def test_list_commit_messages_with_parent(mock_git_output):
    """Test commit messages listing with parent commit"""
    mock_git_output.return_value = b'commit1\nfile1.py\ncommit2\nfile2.py'
    result = list_commit_messages('abc123', 'def456', refer_commit_parent=True)
    assert 'commit1' in result.decode('utf-8')
    assert 'commit2' in result.decode('utf-8')
    mock_git_output.assert_called_once_with(
        ['git', 'log', '--pretty=format:%s', '--name-only', 'abc123^..def456']
    )

def test_list_commits_for_branches_success(mock_git_output):
    """Test successful branch commits listing"""
    result = list_commits_for_branches('branch1', 'branch2')
    assert result == ['file1.py', 'file2.py']
    mock_git_output.assert_called_once_with(
        ['git', 'log', '--pretty=format:%h', 'branch1..branch2']
    )

def test_list_commits_for_tags_success(mock_git_output):
    """Test successful tag commits listing"""
    result = list_commits_for_tags('v1.0.0', 'v1.1.0')
    assert result == ['file1.py', 'file2.py']
    mock_git_output.assert_called_once_with(
        ['git', 'log', '--pretty=format:%h', 'v1.0.0', 'v1.1.0']
    )

def test_list_tags_success(mock_git_output):
    """Test successful tags listing"""
    mock_git_output.return_value = b'v1.0.0\nv1.1.0\nv1.2.0'
    result = list_tags()
    assert result == ['v1.0.0', 'v1.1.0', 'v1.2.0']
    mock_git_output.assert_called_once_with(['git', 'tag'])

def test_run_git_command_success(mock_git_output):
    """Test successful git command execution"""
    result = run_git_command(['git', 'test'])
    assert result == ['file1.py', 'file2.py']
    mock_git_output.assert_called_once_with(['git', 'test'])

def test_run_git_command_empty_output(mock_git_output):
    """Test git command execution with empty output"""
    mock_git_output.return_value = b''
    result = run_git_command(['git', 'test'])
    assert result == []

def test_run_git_command_with_spaces(mock_git_output):
    """Test git command execution with spaces in output"""
    mock_git_output.return_value = b'  file1.py  \n  file2.py  \n'
    result = run_git_command(['git', 'test'])
    assert result == ['file1.py', 'file2.py'] 