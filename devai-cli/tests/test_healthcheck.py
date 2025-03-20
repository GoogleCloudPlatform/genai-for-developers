import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from devai.commands.healthcheck import healthcheck

@pytest.fixture
def mock_generative_model():
    """Fixture to mock Vertex AI GenerativeModel"""
    with patch('devai.commands.healthcheck.GenerativeModel') as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Hello World!"
        mock_model.generate_content = MagicMock(return_value=mock_response)
        mock.return_value = mock_model
        yield mock

@pytest.fixture
def cli_runner():
    """Fixture to provide a CLI runner"""
    return CliRunner()

def test_healthcheck_success(cli_runner, mock_generative_model):
    """Test successful healthcheck"""
    result = cli_runner.invoke(healthcheck)
    
    assert result.exit_code == 0
    assert "Testing Vertex AI connectivity..." in result.output
    assert "Success! Response: Hello World!" in result.output
    assert "Environment Info:" in result.output
    assert "- Model: gemini-pro" in result.output
    mock_generative_model.return_value.generate_content.assert_called_once_with("Say 'Hello World!'")

def test_healthcheck_failure(cli_runner, mock_generative_model):
    """Test healthcheck failure"""
    mock_generative_model.return_value.generate_content.side_effect = Exception("API Error")
    
    result = cli_runner.invoke(healthcheck)
    
    assert result.exit_code == 1
    assert "Testing Vertex AI connectivity..." in result.output
    assert "Error: API Error" in result.output
    mock_generative_model.return_value.generate_content.assert_called_once_with("Say 'Hello World!'") 