import pytest
import os
from pathlib import Path
import yaml
import warnings
import json
from click.testing import CliRunner
from devai.commands.prompts import prompts, get_prompts_dir, set_prompts_dir, CONFIG_FILE, CONFIG_DIR
from unittest.mock import patch, MagicMock

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google._upb._message")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

@pytest.fixture(autouse=True)
def setup_test_config(tmp_path):
    """Setup a temporary config directory for tests."""
    # Store original config path
    original_config_dir = CONFIG_DIR
    original_config_file = CONFIG_FILE
    
    # Set up temporary config directory
    test_config_dir = tmp_path / '.devai'
    test_config_dir.mkdir()
    test_config_file = test_config_dir / 'config.json'
    
    # Update the module's config paths
    import devai.commands.prompts
    devai.commands.prompts.CONFIG_DIR = test_config_dir
    devai.commands.prompts.CONFIG_FILE = test_config_file
    
    yield
    
    # Restore original config paths
    devai.commands.prompts.CONFIG_DIR = original_config_dir
    devai.commands.prompts.CONFIG_FILE = original_config_file

@pytest.fixture
def mock_config():
    """Mock configuration to avoid affecting real settings."""
    with patch('devai.commands.prompts.get_config') as mock_get_config, \
         patch('devai.commands.prompts.save_config') as mock_save_config:
        mock_get_config.return_value = {}
        yield mock_get_config, mock_save_config

@pytest.fixture
def mock_prompts_dir(tmp_path):
    """Mock prompts directory to use temporary directory."""
    with patch('devai.commands.prompts.get_prompts_dir') as mock_get_prompts_dir, \
         patch('devai.commands.prompts.get_user_prompts_dir') as mock_get_user_prompts_dir:
        mock_get_prompts_dir.return_value = tmp_path / 'prompts'
        mock_get_user_prompts_dir.return_value = tmp_path / 'prompts'
        yield mock_get_prompts_dir, mock_get_user_prompts_dir

def test_prompts_command_exists():
    """Test that the prompts command group exists."""
    assert prompts is not None
    # Check that the commands are registered with the group
    assert 'list' in prompts.commands
    assert 'show' in prompts.commands
    assert 'create' in prompts.commands

def test_list_command(tmp_path, mock_prompts_dir):
    """Test the list command."""
    # Create a test prompt file
    prompts_dir = tmp_path / 'prompts'
    security_dir = prompts_dir / 'security'
    security_dir.mkdir(parents=True)
    
    test_prompt = {
        'metadata': {
            'name': 'Test Prompt',
            'description': 'Test description',
            'category': 'security',
            'subcategory': 'test',
            'tags': ['test']
        }
    }
    
    with open(security_dir / 'test.yaml', 'w') as f:
        import yaml
        yaml.dump(test_prompt, f)
    
    # Test listing prompts
    runner = CliRunner()
    result = runner.invoke(prompts, ['list'])
    
    assert result.exit_code == 0
    assert 'Test Prompt' in result.output
    assert 'security' in result.output
    assert 'test' in result.output

def test_show_command(tmp_path, mock_prompts_dir):
    """Test the show command."""
    # Create a test prompt file
    prompts_dir = tmp_path / 'prompts'
    security_dir = prompts_dir / 'security'
    security_dir.mkdir(parents=True)
    
    test_prompt = {
        'metadata': {
            'name': 'Test Prompt',
            'description': 'Test description',
            'category': 'security',
            'subcategory': 'test',
            'tags': ['test']
        },
        'configuration': {
            'temperature': 0.7,
            'max_tokens': 1024,
            'output_format': 'markdown'
        },
        'prompt': {
            'system_context': 'Test context',
            'instruction': 'Test instruction'
        }
    }
    
    with open(security_dir / 'test.yaml', 'w') as f:
        import yaml
        yaml.dump(test_prompt, f)
    
    # Test showing prompt
    runner = CliRunner()
    result = runner.invoke(prompts, ['show', 'security/test.yaml'])
    
    assert result.exit_code == 0
    assert 'Test Prompt' in result.output
    assert 'Test description' in result.output
    assert 'security' in result.output
    assert 'test' in result.output

def test_config_command(tmp_path, mock_config):
    """Test the config command."""
    runner = CliRunner()

    # Test showing current config
    result = runner.invoke(prompts, ['config', '--show'])
    assert result.exit_code == 0
    assert 'Using custom prompts directory' in result.output or 'Using package prompts directory' in result.output

    # Test setting custom path
    custom_path = str(tmp_path / 'custom_prompts')
    result = runner.invoke(prompts, ['config', '--set-path', custom_path])
    assert result.exit_code == 0
    assert f'Custom prompts directory set to: {custom_path}' in result.output

    # Test resetting to package prompts
    result = runner.invoke(prompts, ['config', '--reset'])
    assert result.exit_code == 0
    assert 'Reset to use package prompts' in result.output

def test_init_command(tmp_path, mock_prompts_dir):
    """Test the init command."""
    # Test initialization with force flag
    runner = CliRunner()
    result = runner.invoke(prompts, ['init', '--force'])

    assert result.exit_code == 0
    assert 'Initialized prompts directory' in result.output
    assert 'Created sample template: security/web-security.yaml' in result.output
    assert (tmp_path / 'prompts' / 'security' / 'web-security.yaml').exists()

def test_create_command(tmp_path, mock_prompts_dir):
    """Test the create command."""
    runner = CliRunner()
    
    # Test creating a new prompt
    result = runner.invoke(prompts, ['create'], input='Test Prompt\nsecurity\ntest\nTest description\ntest\n')
    
    assert result.exit_code == 0
    assert 'Created new template' in result.output
    
    # Verify the file was created
    prompt_file = tmp_path / 'prompts' / 'security' / 'test.yaml'
    assert prompt_file.exists()
    
    # Verify the content
    with open(prompt_file, 'r') as f:
        import yaml
        data = yaml.safe_load(f)
        assert data['metadata']['name'] == 'Test Prompt'
        assert data['metadata']['category'] == 'security'
        assert data['metadata']['subcategory'] == 'test'
        assert data['metadata']['description'] == 'Test description'
        assert 'test' in data['metadata']['tags'] 