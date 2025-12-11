"""Test configuration for GitHub module tests."""

import pytest


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
