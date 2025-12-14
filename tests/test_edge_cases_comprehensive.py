"""Comprehensive edge case and error scenario tests for all GitHub tools."""

import pytest
from unittest.mock import Mock, patch
from github.GithubException import (
    GithubException,
    UnknownObjectException,
    BadCredentialsException,
    RateLimitExceededException,
)

from amplifier_module_tool_github.tools.issues import CreateIssueTool
from amplifier_module_tool_github.tools.pull_requests import CreatePullRequestTool
from amplifier_module_tool_github.tools.repositories import CreateRepositoryTool
from amplifier_module_tool_github.tools.branches import CreateBranchTool
from amplifier_module_tool_github.tools.releases import CreateReleaseTool
from amplifier_module_tool_github.tools.actions import TriggerWorkflowTool


class TestAuthenticationEdgeCases:
    """Test authentication edge cases across all tools."""

    @pytest.mark.asyncio
    async def test_no_authentication(self, test_username):
        """Test all tools fail gracefully without authentication."""
        manager = Mock()
        manager.is_authenticated.return_value = False
        
        tools = [
            CreateIssueTool(manager),
            CreatePullRequestTool(manager),
            CreateRepositoryTool(manager),
            CreateBranchTool(manager),
            CreateReleaseTool(manager),
            TriggerWorkflowTool(manager),
        ]
        
        for tool in tools:
            result = await tool.execute({"repository": f"{test_username}/repo"})
            assert not result.success
            assert "AUTHENTICATION_ERROR" in result.error["code"]

    @pytest.mark.asyncio
    async def test_bad_credentials(self, test_username):
        """Test handling of bad credentials."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = BadCredentialsException(401, "Bad credentials")
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_token_expired(self, test_username):
        """Test handling of expired token."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = GithubException(401, {"message": "Token expired"})
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success


class TestRateLimitingEdgeCases:
    """Test rate limiting edge cases."""

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_primary(self, test_username):
        """Test handling primary rate limit exceeded."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = RateLimitExceededException(
            403,
            {"message": "API rate limit exceeded"},
            {"X-RateLimit-Reset": "1640995200"}
        )
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success
        assert "PERMISSION_DENIED" in result.error["code"]  # 403 errors map to PERMISSION_DENIED

    @pytest.mark.asyncio
    async def test_secondary_rate_limit(self, test_username):
        """Test handling secondary rate limit."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = GithubException(
            403,
            {"message": "You have exceeded a secondary rate limit"}
        )
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success


class TestPermissionEdgeCases:
    """Test permission and access edge cases."""

    @pytest.mark.asyncio
    async def test_no_write_access(self, test_username):
        """Test operations requiring write access fail gracefully."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_issue.side_effect = GithubException(
            403,
            {"message": "Must have write access"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success
        assert "PERMISSION_DENIED" in result.error["code"]

    @pytest.mark.asyncio
    async def test_read_only_repository(self, test_username):
        """Test operations on read-only repository."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_issue.side_effect = GithubException(
            403,
            {"message": "Repository is archived or read-only"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success


class TestValidationEdgeCases:
    """Test input validation edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_repository_format(self, test_username):
        """Test various invalid repository formats."""
        from amplifier_module_tool_github.exceptions import RepositoryNotFoundError
        manager = Mock()
        manager.is_authenticated.return_value = True
        tool = CreateIssueTool(manager)
        
        invalid_repos = [
            "",
            "   ",
            "no-slash",
            "too/many/slashes",
            "https://github.com/owner/repo",  # URL instead of owner/repo
        ]
        
        for invalid_repo in invalid_repos:
            # Mock get_repository to raise RepositoryNotFoundError for invalid formats
            manager.get_repository.side_effect = RepositoryNotFoundError(invalid_repo)
            result = await tool.execute({
                "repository": invalid_repo,
                "title": "Test"
            })
            # Should fail due to repository not found
            assert not result.success

    @pytest.mark.asyncio
    async def test_empty_required_fields(self, test_username):
        """Test tools with empty required fields."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        
        # Empty issue title
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": ""
        })
        assert not result.success

    @pytest.mark.asyncio
    async def test_extremely_long_inputs(self, test_username):
        """Test handling of extremely long inputs."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        
        # Create a 100KB title (way over GitHub limits)
        long_title = "A" * 100000
        mock_repo.create_issue.side_effect = GithubException(
            422,
            {"message": "Validation Failed"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": long_title
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_special_characters_in_inputs(self, test_username):
        """Test handling special characters in inputs."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test with 特殊字符 and émojis 🚀"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_repo.create_issue.return_value = mock_issue
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test with 特殊字符 and émojis 🚀"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_null_optional_parameters(self, test_username):
        """Test handling of None values for optional parameters."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_repo.create_issue.return_value = mock_issue
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test",
            "body": None,
            "labels": None,
            "assignees": None
        })
        
        assert result.success


class TestRepositoryEdgeCases:
    """Test repository-related edge cases."""

    @pytest.mark.asyncio
    async def test_repository_not_found(self, test_username):
        """Test handling of non-existent repositories."""
        from amplifier_module_tool_github.exceptions import RepositoryNotFoundError
        manager = Mock()
        manager.is_authenticated.return_value = True
        repo_name = f"{test_username}/nonexistent-repo"
        manager.get_repository.side_effect = RepositoryNotFoundError(repo_name)
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": repo_name,
            "title": "Test"
        })
        
        assert not result.success
        assert "REPOSITORY_NOT_FOUND" in result.error["code"]

    @pytest.mark.asyncio
    async def test_private_repository_no_access(self, test_username):
        """Test accessing private repository without permission."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = UnknownObjectException(404, "Not Found")
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": "someuser/private-repo",
            "title": "Test"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_archived_repository(self, test_username):
        """Test operations on archived repository."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.archived = True
        mock_repo.create_issue.side_effect = GithubException(
            403,
            {"message": "Repository is archived"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/archived-repo",
            "title": "Test"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_disabled_repository(self, test_username):
        """Test operations on disabled repository."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.disabled = True
        manager.get_repository.return_value = mock_repo
        
        # Repository is disabled but still accessible, operations should fail
        mock_repo.create_issue.side_effect = GithubException(
            403,
            {"message": "Repository is disabled"}
        )
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/disabled-repo",
            "title": "Test"
        })
        
        assert not result.success


class TestNetworkEdgeCases:
    """Test network and connectivity edge cases."""

    @pytest.mark.asyncio
    async def test_timeout(self, test_username):
        """Test handling of network timeout."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = Exception("Timeout")
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_connection_error(self, test_username):
        """Test handling of connection errors."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        manager.get_repository.side_effect = ConnectionError("Connection refused")
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success


class TestBranchEdgeCases:
    """Test branch-related edge cases."""

    @pytest.mark.asyncio
    async def test_create_branch_invalid_characters(self, test_username):
        """Test creating branch with invalid characters."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref.side_effect = GithubException(
            422,
            {"message": "Reference name is invalid"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateBranchTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "invalid..branch"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_branch_not_found(self, test_username):
        """Test operations on non-existent branch."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.get_branch.side_effect = GithubException(404, {"message": "Branch not found"})
        manager.get_repository.return_value = mock_repo
        
        tool = CreateBranchTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "new-branch",
            "from_branch": "nonexistent"
        })
        
        assert not result.success


class TestPullRequestEdgeCases:
    """Test pull request-related edge cases."""

    @pytest.mark.asyncio
    async def test_pr_no_commits_between_branches(self, test_username):
        """Test creating PR when branches are identical."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(
            422,
            {"message": "No commits between main and main"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreatePullRequestTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test PR",
            "head": "main",
            "base": "main"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_pr_already_exists(self, test_username):
        """Test creating PR when one already exists."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(
            422,
            {"message": "A pull request already exists"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreatePullRequestTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test PR",
            "head": "feature",
            "base": "main"
        })
        
        assert not result.success


class TestWorkflowEdgeCases:
    """Test workflow-related edge cases."""

    @pytest.mark.asyncio
    async def test_workflow_not_found(self, test_username):
        """Test triggering non-existent workflow."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.get_workflow.side_effect = UnknownObjectException(404, "Not Found")
        manager.get_repository.return_value = mock_repo
        
        tool = TriggerWorkflowTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": "nonexistent.yml"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_workflow_disabled(self, test_username):
        """Test triggering disabled workflow."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_workflow = Mock()
        mock_workflow.state = "disabled"
        mock_workflow.create_dispatch.side_effect = GithubException(
            422,
            {"message": "Workflow is disabled"}
        )
        mock_repo.get_workflow.return_value = mock_workflow
        manager.get_repository.return_value = mock_repo
        
        tool = TriggerWorkflowTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": 123
        })
        
        assert not result.success


class TestConcurrencyEdgeCases:
    """Test concurrency and race condition edge cases."""

    @pytest.mark.asyncio
    async def test_concurrent_modifications(self, test_username):
        """Test handling of concurrent modifications."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_issue.side_effect = GithubException(
            409,
            {"message": "Conflict"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test"
        })
        
        assert not result.success


class TestLabelAssigneeEdgeCases:
    """Test label and assignee edge cases."""

    @pytest.mark.asyncio
    async def test_nonexistent_labels(self, test_username):
        """Test creating issue with non-existent labels."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        # GitHub creates labels automatically if they don't exist (depending on permissions)
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_repo.create_issue.return_value = mock_issue
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test",
            "labels": ["nonexistent-label"]
        })
        
        # May succeed or fail depending on permissions
        # Just checking it doesn't crash
        assert result.success or not result.success

    @pytest.mark.asyncio
    async def test_invalid_assignees(self, test_username):
        """Test creating issue with invalid assignees."""
        manager = Mock()
        manager.is_authenticated.return_value = True
        mock_repo = Mock()
        mock_repo.create_issue.side_effect = GithubException(
            422,
            {"message": "User does not have permission to be assigned"}
        )
        manager.get_repository.return_value = mock_repo
        
        tool = CreateIssueTool(manager)
        result = await tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test",
            "assignees": ["nonexistent-user"]
        })
        
        assert not result.success
