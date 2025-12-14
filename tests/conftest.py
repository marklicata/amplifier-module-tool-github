"""Test configuration for GitHub module tests."""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock


def create_mock_datetime(date_string):
    """Create a mock datetime object that can be used in tests."""
    mock_dt = Mock()
    mock_dt.isoformat.return_value = date_string
    mock_dt.__str__ = lambda self: date_string
    return mock_dt


@pytest.fixture
def mock_github_config():
    """Mock configuration for GitHub manager."""
    return {
        "token": "ghp_test_token_123456789",
        "base_url": "https://api.github.com"
    }


@pytest.fixture
def mock_repository_name():
    """Mock repository name."""
    return "test-owner/test-repo"


@pytest.fixture
def test_username():
    """
    Get test username from environment or use default.
    
    This fixture allows tests to use the actual authenticated user's username
    instead of hardcoded values. Set GITHUB_TEST_USERNAME environment variable
    to override the default.
    """
    return os.environ.get("GITHUB_TEST_USERNAME", "test-user")
