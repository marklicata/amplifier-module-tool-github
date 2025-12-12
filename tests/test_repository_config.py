"""Tests for repository configuration and access control."""

import pytest
from amplifier_module_tool_github.manager import GitHubManager


class TestRepositoryConfiguration:
    """Tests for repository configuration parsing and validation."""

    def test_parse_https_url(self):
        """Test parsing HTTPS GitHub URLs."""
        config = {
            "repositories": [
                "https://github.com/microsoft/vscode",
                "https://github.com/python/cpython.git",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 2
        assert "microsoft/vscode" in repos
        assert "python/cpython" in repos

    def test_parse_ssh_url(self):
        """Test parsing SSH GitHub URLs."""
        config = {
            "repositories": [
                "git@github.com:microsoft/vscode.git",
                "git@github.com:python/cpython",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 2
        assert "microsoft/vscode" in repos
        assert "python/cpython" in repos

    def test_parse_owner_repo_format(self):
        """Test parsing owner/repo format."""
        config = {
            "repositories": [
                "microsoft/vscode",
                "python/cpython",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 2
        assert "microsoft/vscode" in repos
        assert "python/cpython" in repos

    def test_parse_mixed_formats(self):
        """Test parsing mixed URL and owner/repo formats."""
        config = {
            "repositories": [
                "https://github.com/microsoft/vscode",
                "git@github.com:python/cpython.git",
                "facebook/react",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 3
        assert "microsoft/vscode" in repos
        assert "python/cpython" in repos
        assert "facebook/react" in repos

    def test_normalize_repository_https(self):
        """Test normalizing HTTPS URLs."""
        manager = GitHubManager({})
        
        assert manager._normalize_repository("https://github.com/owner/repo") == "owner/repo"
        assert manager._normalize_repository("https://github.com/owner/repo.git") == "owner/repo"
        assert manager._normalize_repository("https://github.com/owner/repo/") == "owner/repo"

    def test_normalize_repository_ssh(self):
        """Test normalizing SSH URLs."""
        manager = GitHubManager({})
        
        assert manager._normalize_repository("git@github.com:owner/repo.git") == "owner/repo"
        assert manager._normalize_repository("git@github.com:owner/repo") == "owner/repo"

    def test_normalize_repository_direct(self):
        """Test normalizing direct owner/repo format."""
        manager = GitHubManager({})
        
        assert manager._normalize_repository("owner/repo") == "owner/repo"
        assert manager._normalize_repository("  owner/repo  ") == "owner/repo"

    def test_normalize_repository_invalid(self):
        """Test normalizing invalid repository identifiers."""
        manager = GitHubManager({})
        
        assert manager._normalize_repository("invalid") is None
        assert manager._normalize_repository("") is None
        assert manager._normalize_repository("   ") is None
        assert manager._normalize_repository("owner/repo/extra") is None

    def test_duplicate_repositories(self):
        """Test that duplicate repositories are deduplicated."""
        config = {
            "repositories": [
                "https://github.com/microsoft/vscode",
                "git@github.com:microsoft/vscode.git",
                "microsoft/vscode",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 1
        assert "microsoft/vscode" in repos

    def test_is_repository_allowed_no_config(self):
        """Test that all repositories are allowed when no config is set."""
        manager = GitHubManager({})
        
        assert manager.is_repository_allowed("microsoft/vscode")
        assert manager.is_repository_allowed("python/cpython")
        assert manager.is_repository_allowed("any/repo")

    def test_is_repository_allowed_with_config(self):
        """Test repository access control with configured repositories."""
        config = {
            "repositories": [
                "microsoft/vscode",
                "python/cpython",
            ]
        }
        manager = GitHubManager(config)
        
        # Allowed repositories
        assert manager.is_repository_allowed("microsoft/vscode")
        assert manager.is_repository_allowed("python/cpython")
        
        # Not allowed
        assert not manager.is_repository_allowed("facebook/react")
        assert not manager.is_repository_allowed("other/repo")

    def test_is_repository_allowed_url_formats(self):
        """Test that various URL formats are accepted for access checks."""
        config = {
            "repositories": ["microsoft/vscode"]
        }
        manager = GitHubManager(config)
        
        # All these should resolve to microsoft/vscode and be allowed
        assert manager.is_repository_allowed("microsoft/vscode")
        assert manager.is_repository_allowed("https://github.com/microsoft/vscode")
        assert manager.is_repository_allowed("git@github.com:microsoft/vscode.git")

    def test_restrict_to_configured_flag(self):
        """Test the restrict_to_configured flag."""
        # No repositories configured
        manager1 = GitHubManager({})
        assert not manager1.restrict_to_configured
        
        # Empty list
        manager2 = GitHubManager({"repositories": []})
        assert not manager2.restrict_to_configured
        
        # With repositories
        manager3 = GitHubManager({"repositories": ["microsoft/vscode"]})
        assert manager3.restrict_to_configured

    def test_get_configured_repositories_empty(self):
        """Test getting configured repositories when none are set."""
        manager = GitHubManager({})
        
        repos = manager.get_configured_repositories()
        assert repos == []

    def test_get_configured_repositories_sorted(self):
        """Test that configured repositories are returned sorted."""
        config = {
            "repositories": [
                "zebra/repo",
                "apple/repo",
                "microsoft/vscode",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert repos == ["apple/repo", "microsoft/vscode", "zebra/repo"]

    def test_github_enterprise_urls(self):
        """Test parsing GitHub Enterprise URLs."""
        config = {
            "base_url": "https://github.company.com/api/v3",
            "repositories": [
                "https://github.company.com/owner/repo",
                "https://github.company.com/owner/repo.git",
            ]
        }
        manager = GitHubManager(config)
        
        repos = manager.get_configured_repositories()
        assert len(repos) == 1
        assert "owner/repo" in repos
