import pytest
import os
import sys
import warnings

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google._upb._message")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_example():
    """
    Example test to demonstrate the test harness setup.
    This test should always pass.
    """
    assert True, "This test should always pass"

def test_environment():
    """
    Test to verify the test environment is properly set up.
    """
    # Verify we can import from the src directory
    try:
        # This will fail if the src directory is not in the Python path
        from devai import cli
        assert cli is not None
    except ImportError as e:
        pytest.fail(f"Failed to import from src directory: {e}") 