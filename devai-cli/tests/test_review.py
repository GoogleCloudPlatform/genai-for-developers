import pytest
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from devai.commands.review import (
    ensure_env_variable,
    get_prompt,
    load_image_from_path,
    validate_and_correct_json,
    code,
    review
)
from vertexai.generative_models import Image, GenerativeModel, Part, Content
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, PermissionDenied
import os
import json
import pathlib
from rich.console import Console
from rich.table import Table

@pytest.fixture
def mock_env():
    """Fixture to mock environment variables"""
    with patch.dict(os.environ, {
        'TEST_VAR': 'test_value',
        'PROJECT_ID': 'test-project',
        'LOCATION': 'test-location'
    }):
        yield

@pytest.fixture
def mock_secret_manager():
    """Fixture to mock Secret Manager client"""
    with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = 'test_prompt'
        mock_instance.access_secret_version.return_value = mock_response
        yield mock_instance

@pytest.fixture(autouse=True)
def mock_image_class():
    """Mock the Image class"""
    with patch('devai.commands.review.Image') as mock:
        mock_instance = Part.from_data(data=b'test data', mime_type='image/jpeg')
        mock.load_from_file.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_generative_model():
    """Mock the GenerativeModel class"""
    with patch('devai.commands.review.GenerativeModel') as mock:
        mock_instance = MagicMock()
        mock_response = MagicMock(text='Test response')

        def generate_content(*args, **kwargs):
            if kwargs.get('stream', False):
                return [mock_response]
            return mock_response

        mock_instance.generate_content.side_effect = generate_content
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_rich():
    """Fixture to mock rich console and table"""
    with patch('rich.console.Console') as mock_console, \
         patch('rich.table.Table') as mock_table:
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        yield mock_console_instance, mock_table_instance

@pytest.fixture
def mock_part():
    """Mock the Part class"""
    with patch('devai.commands.review.Part') as mock:
        mock_instance = Part.from_data(data=b'test data', mime_type='video/mp4')
        mock.from_data.return_value = mock_instance
        yield mock

@pytest.fixture
def test_image_data():
    """Test image data - minimal PNG file"""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82'

@pytest.fixture
def test_video_data():
    """Test video data - minimal MP4 file"""
    return b'\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x01moov'

@pytest.fixture
def cli_runner():
    """Fixture for Click CLI testing"""
    return CliRunner()

@pytest.fixture
def mock_path():
    """Mock pathlib.Path operations"""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.read_bytes', return_value=b'test data'):
        yield

def test_ensure_env_variable_success(mock_env):
    """Test successful environment variable retrieval"""
    assert ensure_env_variable('TEST_VAR') == 'test_value'

def test_ensure_env_variable_missing():
    """Test missing environment variable"""
    with pytest.raises(EnvironmentError) as exc:
        ensure_env_variable('NONEXISTENT_VAR')
    assert "Required environment variable 'NONEXISTENT_VAR' is not set" in str(exc.value)

def test_get_prompt_success(mock_env, mock_secret_manager):
    """Test successful prompt retrieval"""
    result = get_prompt('test-secret')
    assert result == 'test_prompt'
    mock_secret_manager.access_secret_version.assert_called_once_with(
        name='projects/test-project/secrets/test-secret/versions/latest'
    )

def test_get_prompt_permission_denied(mock_env, mock_secret_manager):
    """Test permission denied error"""
    mock_secret_manager.access_secret_version.side_effect = PermissionDenied('test')
    result = get_prompt('test-secret')
    assert result is None

def test_get_prompt_not_found(mock_env, mock_secret_manager):
    """Test secret not found error"""
    mock_secret_manager.access_secret_version.side_effect = NotFound('test')
    result = get_prompt('test-secret')
    assert result is None

def test_get_prompt_missing_project_id():
    """Test missing project ID"""
    with patch.dict(os.environ, {}, clear=True):
        result = get_prompt('test-secret')
        assert result is None

def test_load_image_from_path_success(mock_image_class, test_image_data):
    """Test successful image loading"""
    with patch('pathlib.Path.read_bytes', return_value=test_image_data):
        result = load_image_from_path('test.jpg')
        mock_image_class.load_from_file.assert_called_once_with('test.jpg')
        assert result == mock_image_class.load_from_file.return_value

def test_validate_and_correct_json_valid():
    """Test validation of valid JSON"""
    valid_json = '{"key": "value"}'
    result = validate_and_correct_json(valid_json)
    assert result == valid_json
    assert json.loads(result) == {"key": "value"}

def test_validate_and_correct_json_invalid_repairable():
    """Test correction of invalid but repairable JSON"""
    invalid_json = '{key: "value"}'  # Missing quotes around key
    with patch('json_repair.repair_json') as mock_repair:
        mock_repair.return_value = '{"key": "value"}'
        result = validate_and_correct_json(invalid_json)
        assert result is not None
        assert json.loads(result) == {"key": "value"}

def test_validate_and_correct_json_invalid_unrepairable():
    """Test handling of invalid and unrepairable JSON"""
    with patch('json_repair.repair_json', side_effect=ValueError('Invalid JSON')):
        invalid_json = 'completely invalid json'
        result = validate_and_correct_json(invalid_json)
        assert result == '""'

def test_code_command_no_context(cli_runner, mock_env, mock_generative_model, mock_rich):
    """Test code review command with no context"""
    result = cli_runner.invoke(code, [])
    assert result.exit_code == 0

def test_code_command_with_context(cli_runner, mock_env, mock_generative_model, mock_rich):
    """Test code review command with context"""
    result = cli_runner.invoke(code, ['-c', 'def test(): pass'])
    assert result.exit_code == 0

def test_code_command_with_output_format(cli_runner, mock_env, mock_generative_model, mock_rich):
    """Test code review command with different output formats"""
    formats = ['markdown', 'json', 'table']
    for fmt in formats:
        result = cli_runner.invoke(code, ['-o', fmt])
        assert result.exit_code == 0

def test_review_group(cli_runner):
    """Test review command group"""
    result = cli_runner.invoke(review, ['--help'])
    assert result.exit_code == 0
    assert 'code' in result.output
    assert 'performance' in result.output
    assert 'security' in result.output

def test_performance_command(cli_runner, mock_env, mock_generative_model):
    """Test performance review command"""
    result = cli_runner.invoke(review, ['performance', '-c', 'def test(): pass'])
    assert result.exit_code == 0

def test_security_command(cli_runner, mock_env, mock_generative_model):
    """Test security review command"""
    result = cli_runner.invoke(review, ['security', '-c', 'def test(): pass'])
    assert result.exit_code == 0

def test_testcoverage_command(cli_runner, mock_env, mock_generative_model):
    """Test test coverage review command"""
    result = cli_runner.invoke(review, ['testcoverage', '-c', 'def test(): pass'])
    assert result.exit_code == 0

def test_blockers_command(cli_runner, mock_env, mock_generative_model):
    """Test blockers review command"""
    result = cli_runner.invoke(review, ['blockers', '-c', 'def test(): pass'])
    assert result.exit_code == 0

def test_impact_command(cli_runner, mock_env, mock_generative_model):
    """Test impact analysis command"""
    result = cli_runner.invoke(review, ['impact', '-c', 'def test(): pass', '-t', 'def test(): pass'])
    assert result.exit_code == 0

def test_imgdiff_command(cli_runner, mock_env, mock_generative_model, mock_image_class, test_image_data):
    """Test image diff command"""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.read_bytes', return_value=test_image_data), \
         patch('devai.commands.review.get_prompt', return_value='Test prompt'):
        result = cli_runner.invoke(review, ['imgdiff', '-c', 'test1.jpg', '-t', 'test2.jpg'])
        assert result.exit_code == 0
        assert 'Test response' in result.output

def test_image_command(cli_runner, mock_env, mock_generative_model, mock_image_class, test_image_data):
    """Test image analysis command"""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.read_bytes', return_value=test_image_data), \
         patch('devai.commands.review.get_prompt', return_value='Test prompt'):
        result = cli_runner.invoke(review, ['image', '-f', 'test.jpg', '-p', 'What is in this image?'])
        assert result.exit_code == 0
        assert 'Test response' in result.output

def test_video_command(cli_runner, mock_env, mock_generative_model, mock_part, test_video_data):
    """Test video analysis command"""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=test_video_data)), \
         patch('devai.commands.review.get_prompt', return_value='Test prompt'):
        result = cli_runner.invoke(review, ['video', '-f', 'test.mp4', '-p', 'What is in this video?'])
        assert result.exit_code == 0
        assert 'Test response' in result.output

def test_compliance_command(cli_runner, mock_env, mock_generative_model):
    """Test compliance review command"""
    result = cli_runner.invoke(review, ['compliance', '-c', 'def test(): pass', '-cfg', '.gemini'])
    assert result.exit_code == 0 