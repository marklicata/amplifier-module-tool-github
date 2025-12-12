"""Tests for GitHubManager."""

import pytest
import os
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
        """Test starting manager without token when all auth methods disabled."""
        with patch.dict(os.environ, {}, clear=True):
            manager = GitHubManager({"use_cli_auth": False, "prompt_if_missing": False})
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

    def test_get_token_from_environment(self):
        """Test getting token from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token_123"}):
            manager = GitHubManager({})
            token = manager._get_token_from_sources()
            assert token == "env_token_123"

    def test_get_token_from_gh_token_env(self):
        """Test getting token from GH_TOKEN environment variable."""
        with patch.dict(os.environ, {"GH_TOKEN": "gh_env_token_456"}, clear=True):
            manager = GitHubManager({})
            token = manager._get_token_from_sources()
            assert token == "gh_env_token_456"

    def test_get_token_from_cli(self):
        """Test getting token from GitHub CLI."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "cli_token_789\n"
        
        with patch("subprocess.run", return_value=mock_result):
            manager = GitHubManager({"use_cli_auth": True})
            token = manager._get_token_from_cli()
            assert token == "cli_token_789"

    def test_get_token_from_cli_not_authenticated(self):
        """Test GitHub CLI not authenticated."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "not authenticated"
        
        with patch("subprocess.run", return_value=mock_result):
            manager = GitHubManager({"use_cli_auth": True})
            token = manager._get_token_from_cli()
            assert token is None

    def test_get_token_from_cli_not_installed(self):
        """Test GitHub CLI not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager = GitHubManager({"use_cli_auth": True})
            token = manager._get_token_from_cli()
            assert token is None

    def test_get_token_priority_config_over_env(self):
        """Test that explicit config token takes priority over environment."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            manager = GitHubManager({"token": "config_token"})
            # Config token should be used directly, not from sources
            assert manager.token == "config_token"

    def test_get_token_priority_env_over_cli(self):
        """Test that environment token takes priority over CLI."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "cli_token"
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            with patch("subprocess.run", return_value=mock_result):
                manager = GitHubManager({})
                token = manager._get_token_from_sources()
                assert token == "env_token"

    def test_cli_auth_disabled(self):
        """Test that CLI auth can be disabled."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "cli_token"
        
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            manager = GitHubManager({"use_cli_auth": False})
            token = manager._get_token_from_sources()
            assert token is None
            mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_with_environment_token(self):
        """Test starting manager with token from environment."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("amplifier_module_tool_github.manager.Github") as mock_github_class:
                with patch("amplifier_module_tool_github.manager.Auth") as mock_auth_class:
                    mock_client = Mock()
                    mock_user = Mock()
                    mock_user.login = "testuser"
                    mock_client.get_user.return_value = mock_user
                    mock_github_class.return_value = mock_client
                    
                    manager = GitHubManager({"prompt_if_missing": False})
                    await manager.start()
                    
                    assert manager.token == "test_token"
                    assert manager.client is not None
                    mock_auth_class.Token.assert_called_once_with("test_token")

    @pytest.mark.asyncio
    async def test_start_no_auth_no_prompt(self):
        """Test starting manager without auth and prompting disabled."""
        with patch.dict(os.environ, {}, clear=True):
            manager = GitHubManager({"prompt_if_missing": False, "use_cli_auth": False})
            await manager.start()
            assert manager.client is None


# Note: Additional tests would require mocking PyGithub more extensively
# or using integration tests with a test GitHub instance
