import pytest
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from devai.commands.prompt import (
    prompt, load_prompt_template, format_prompt,
    template, with_context
)
import os
import yaml

@pytest.fixture
def mock_generative_model():
    """Fixture to mock Vertex AI GenerativeModel"""
    with patch('devai.commands.prompt.GenerativeModel') as mock:
        mock_instance = MagicMock()
        mock_instance.generate_content = MagicMock(return_value=MagicMock(text="Test response"))
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_file_processor():
    """Fixture to mock file processor"""
    with patch('devai.commands.prompt.get_text_files_contents') as mock:
        mock.return_value = {"test.py": "def test(): pass"}
        yield mock

@pytest.fixture
def sample_template():
    """Fixture to provide a sample YAML template"""
    return {
        'prompt': {
            'system_context': 'You are a code reviewer',
            'instruction': 'Review the following code'
        }
    }

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_load_prompt_template_success(sample_template):
    """Test successful template loading"""
    template_yaml = yaml.dump(sample_template)
    with patch('builtins.open', mock_open(read_data=template_yaml)):
        result = load_prompt_template('test.yaml')
        assert result == sample_template

def test_load_prompt_template_file_not_found():
    """Test template loading with missing file"""
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = load_prompt_template('nonexistent.yaml')
        assert result is None

def test_load_prompt_template_invalid_yaml():
    """Test template loading with invalid YAML"""
    with patch('builtins.open', mock_open(read_data='invalid: yaml: :')):
        result = load_prompt_template('invalid.yaml')
        assert result is None

def test_format_prompt_success(sample_template):
    """Test successful prompt formatting"""
    context = "test code"
    result = format_prompt(sample_template, context)
    assert "You are a code reviewer" in result
    assert "Review the following code" in result
    assert "test code" in result

def test_format_prompt_no_template():
    """Test prompt formatting with no template"""
    result = format_prompt(None, "test code")
    assert result is None

def test_template_command_success(cli_runner, mock_generative_model, sample_template):
    """Test successful template command execution"""
    template_yaml = yaml.dump(sample_template)
    with patch('builtins.open', mock_open(read_data=template_yaml)):
        result = cli_runner.invoke(template, ['-t', 'test.yaml', '-c', 'test code'])
        
        assert result.exit_code == 0
        assert "Using template: test.yaml" in result.output
        assert "Test response" in result.output
        mock_generative_model.generate_content.assert_called_once()

def test_template_command_with_directory(cli_runner, mock_generative_model, mock_file_processor, sample_template):
    """Test template command with directory context"""
    template_yaml = yaml.dump(sample_template)
    with patch('builtins.open', mock_open(read_data=template_yaml)):
        result = cli_runner.invoke(template, ['-t', 'test.yaml', '-c', './src'])
        
        assert result.exit_code == 0
        mock_file_processor.assert_called_once()
        mock_generative_model.generate_content.assert_called_once()

def test_template_command_invalid_template(cli_runner):
    """Test template command with invalid template"""
    with patch('builtins.open', mock_open(read_data='invalid: yaml: :')):
        result = cli_runner.invoke(template, ['-t', 'invalid.yaml', '-c', 'test code'])
        
        assert result.exit_code == 0  # Click returns 0 for handled errors
        assert "Error loading template" in result.output

def test_with_context_command_success(cli_runner, mock_generative_model):
    """Test successful with_context command execution"""
    result = cli_runner.invoke(with_context, ['-q', 'test query', '-c', 'test code'])
    
    assert result.exit_code == 0
    assert "Prompt with context" in result.output
    assert "Test response" in result.output
    mock_generative_model.generate_content.assert_called_once()

def test_with_context_command_with_directory(cli_runner, mock_generative_model, mock_file_processor):
    """Test with_context command with directory context"""
    result = cli_runner.invoke(with_context, ['-q', 'test query', '-c', './src'])
    
    assert result.exit_code == 0
    mock_file_processor.assert_called_once()
    mock_generative_model.generate_content.assert_called_once()

def test_prompt_group():
    """Test prompt command group structure"""
    assert prompt.name == 'prompt'
    assert 'template' in prompt.commands
    assert 'with_context' in prompt.commands
    assert 'with-msg-streaming' in prompt.commands
    assert 'with-msg' in prompt.commands 