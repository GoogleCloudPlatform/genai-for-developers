import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from devai.commands.msg.standard import with_msg
from devai.commands.msg.streaming import with_msg_streaming

@pytest.fixture
def mock_generative_model():
    """Fixture to mock Vertex AI GenerativeModel"""
    with patch('devai.commands.msg.standard.GenerativeModel') as mock_standard, \
         patch('devai.commands.msg.streaming.GenerativeModel') as mock_streaming:
        # Setup standard model
        standard_instance = MagicMock()
        standard_instance.generate_content = MagicMock(return_value=MagicMock(text="Test response"))
        mock_standard.return_value = standard_instance
        
        # Setup streaming model
        streaming_instance = MagicMock()
        streaming_instance.generate_content = MagicMock(return_value=[
            MagicMock(text="Test "),
            MagicMock(text="response")
        ])
        mock_streaming.return_value = streaming_instance
        
        yield standard_instance, streaming_instance

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_with_msg_success(cli_runner, mock_generative_model):
    """Test successful standard message command"""
    standard_model, _ = mock_generative_model
    result = cli_runner.invoke(with_msg, ['-q', 'test query'])
    
    assert result.exit_code == 0
    assert "Prompt" in result.output
    assert "Test response" in result.output
    standard_model.generate_content.assert_called_once_with("test query")

def test_with_msg_default_query(cli_runner, mock_generative_model):
    """Test standard message command with default query"""
    standard_model, _ = mock_generative_model
    result = cli_runner.invoke(with_msg)
    
    assert result.exit_code == 0
    assert "Prompt" in result.output
    assert "Test response" in result.output
    standard_model.generate_content.assert_called_once_with("Hello")

def test_with_msg_streaming_success(cli_runner, mock_generative_model):
    """Test successful streaming message command"""
    _, streaming_model = mock_generative_model
    result = cli_runner.invoke(with_msg_streaming, ['-q', 'test query'])
    
    assert result.exit_code == 0
    assert "Prompt with streaming" in result.output
    assert "Test response" in result.output
    streaming_model.generate_content.assert_called_once_with("test query", stream=True)

def test_with_msg_streaming_default_query(cli_runner, mock_generative_model):
    """Test streaming message command with default query"""
    _, streaming_model = mock_generative_model
    result = cli_runner.invoke(with_msg_streaming)
    
    assert result.exit_code == 0
    assert "Prompt with streaming" in result.output
    assert "Test response" in result.output
    streaming_model.generate_content.assert_called_once_with("Hello", stream=True)

def test_with_msg_streaming_empty_response(cli_runner, mock_generative_model):
    """Test streaming message command with empty response"""
    _, streaming_model = mock_generative_model
    streaming_model.generate_content.return_value = []
    result = cli_runner.invoke(with_msg_streaming, ['-q', 'test query'])
    
    assert result.exit_code == 0
    assert "Prompt with streaming" in result.output
    assert result.output.strip() == "Prompt with streaming" 