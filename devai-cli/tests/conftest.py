import pytest
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def test_data_dir():
    """Fixture to provide the path to test data directory."""
    return os.path.join(os.path.dirname(__file__), 'test_data')

@pytest.fixture
def sample_prompt_file(test_data_dir):
    """Fixture to provide a path to a sample prompt file."""
    return os.path.join(test_data_dir, 'sample_prompt.yaml') 