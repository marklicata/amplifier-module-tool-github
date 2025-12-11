"""Tests for GitHubManager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from amplifier_module_tool_github.manager import GitHubManager
from amplifier_module_tool_github.exceptions import (
    AuthenticationError,
    RepositoryNotFoundError,
)


class TestGitHubManager:
    """Tests for GitHubManager class."""

    def test_init_without_pygithub(self):
        """Test initialization when PyGithub is not installed."""
        with patch("amplifier_module_tool_github.manager.Github", None):
            with pytest.raises(ImportError, match="PyGithub is not installed"):
                GitHubManager({"token": "test"})

    def test_init_with_config(self, mock_github_config):
        """Test initialization with configuration."""
        manager = GitHubManager(mock_github_config)
        assert manager.token == mock_github_config["token"]
        assert manager.base_url == mock_github_config["base_url"]
        assert manager.client is None

    @pytest.mark.asyncio
    async def test_start_without_token(self):
        """Test starting manager without token."""
        manager = GitHubManager({})
        await manager.start()
        assert manager.client is None

    @pytest.mark.asyncio
    async def test_stop(self, mock_github_config):
        """Test stopping manager."""
        manager = GitHubManager(mock_github_config)
        manager.client = Mock()
        manager.client.close = Mock()
        await manager.stop()
        manager.client.close.assert_called_once()

    def test_is_authenticated(self, mock_github_config):
        """Test authentication check."""
        manager = GitHubManager(mock_github_config)
        assert not manager.is_authenticated()
        manager.client = Mock()
        assert manager.is_authenticated()


# Note: Additional tests would require mocking PyGithub more extensively
# or using integration tests with a test GitHub instance
