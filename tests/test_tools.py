"""Tests for GitHub tools."""

import pytest
from unittest.mock import Mock, AsyncMock
from amplifier_module_tool_github.tools import (
    # Issues
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
    # Pull Requests
    ListPullRequestsTool,
    GetPullRequestTool,
    CreatePullRequestTool,
    UpdatePullRequestTool,
    MergePullRequestTool,
    ReviewPullRequestTool,
    # Repositories
    GetRepositoryTool,
    ListRepositoriesTool,
    CreateRepositoryTool,
    GetFileContentTool,
    ListRepositoryContentsTool,
    # Commits
    ListCommitsTool,
    GetCommitTool,
    # Branches
    ListBranchesTool,
    GetBranchTool,
    CreateBranchTool,
    CompareBranchesTool,
    # Releases
    ListReleasesTool,
    GetReleaseTool,
    CreateReleaseTool,
    ListTagsTool,
    CreateTagTool,
    # Actions
    ListWorkflowsTool,
    GetWorkflowTool,
    TriggerWorkflowTool,
    ListWorkflowRunsTool,
    GetWorkflowRunTool,
    CancelWorkflowRunTool,
    RerunWorkflowTool,
)


class TestListIssuesTool:
    """Tests for ListIssuesTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListIssuesTool(manager)
        
        assert tool.name == "github_list_issues"
        assert "list issues" in tool.description.lower()
        assert tool.input_schema["type"] == "object"
        assert "repository" in tool.input_schema["properties"]

    @pytest.mark.asyncio
    async def test_execute_without_auth(self):
        """Test execution without authentication."""
        manager = Mock()
        manager.is_authenticated.return_value = False
        tool = ListIssuesTool(manager)
        
        result = await tool.execute({"repository": "test/repo"})
        assert not result.success
        assert "authentication" in result.error["code"].lower()


class TestGetIssueTool:
    """Tests for GetIssueTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = GetIssueTool(manager)
        
        assert tool.name == "github_get_issue"
        assert "get" in tool.description.lower()
        assert "issue" in tool.description.lower()
        assert tool.input_schema["type"] == "object"


class TestCreateIssueTool:
    """Tests for CreateIssueTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CreateIssueTool(manager)
        
        assert tool.name == "github_create_issue"
        assert "create" in tool.description.lower()
        assert tool.input_schema["type"] == "object"
        assert "title" in tool.input_schema["required"]


class TestUpdateIssueTool:
    """Tests for UpdateIssueTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = UpdateIssueTool(manager)
        
        assert tool.name == "github_update_issue"
        assert "update" in tool.description.lower()
        assert tool.input_schema["type"] == "object"


class TestCommentIssueTool:
    """Tests for CommentIssueTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CommentIssueTool(manager)
        
        assert tool.name == "github_comment_issue"
        assert "comment" in tool.description.lower()
        assert tool.input_schema["type"] == "object"
        assert "body" in tool.input_schema["required"]


# Pull Requests Tests
class TestListPullRequestsTool:
    """Tests for ListPullRequestsTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListPullRequestsTool(manager)
        
        assert tool.name == "github_list_pull_requests"
        assert "pull request" in tool.description.lower()
        assert tool.input_schema["type"] == "object"
        assert "repository" in tool.input_schema["properties"]

    @pytest.mark.asyncio
    async def test_execute_without_auth(self):
        """Test execution without authentication."""
        manager = Mock()
        manager.is_authenticated.return_value = False
        tool = ListPullRequestsTool(manager)
        
        result = await tool.execute({"repository": "test/repo"})
        assert not result.success


class TestGetPullRequestTool:
    """Tests for GetPullRequestTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = GetPullRequestTool(manager)
        
        assert tool.name == "github_get_pull_request"
        assert "pull request" in tool.description.lower()
        assert "pull_number" in tool.input_schema["required"]


class TestCreatePullRequestTool:
    """Tests for CreatePullRequestTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CreatePullRequestTool(manager)
        
        assert tool.name == "github_create_pull_request"
        assert "create" in tool.description.lower()
        assert "head" in tool.input_schema["required"]
        assert "base" in tool.input_schema["required"]


class TestMergePullRequestTool:
    """Tests for MergePullRequestTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = MergePullRequestTool(manager)
        
        assert tool.name == "github_merge_pull_request"
        assert "merge" in tool.description.lower()
        assert "merge_method" in tool.input_schema["properties"]


# Repository Tests
class TestGetRepositoryTool:
    """Tests for GetRepositoryTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = GetRepositoryTool(manager)
        
        assert tool.name == "github_get_repository"
        assert "repository" in tool.description.lower()


class TestListRepositoriesTool:
    """Tests for ListRepositoriesTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListRepositoriesTool(manager)
        
        assert tool.name == "github_list_repositories"
        assert "owner" in tool.input_schema["required"]


class TestCreateRepositoryTool:
    """Tests for CreateRepositoryTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CreateRepositoryTool(manager)
        
        assert tool.name == "github_create_repository"
        assert "name" in tool.input_schema["required"]
        assert "private" in tool.input_schema["properties"]


class TestGetFileContentTool:
    """Tests for GetFileContentTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = GetFileContentTool(manager)
        
        assert tool.name == "github_get_file_content"
        assert "path" in tool.input_schema["required"]


# Commit Tests
class TestListCommitsTool:
    """Tests for ListCommitsTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListCommitsTool(manager)
        
        assert tool.name == "github_list_commits"
        assert "commit" in tool.description.lower()


class TestGetCommitTool:
    """Tests for GetCommitTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = GetCommitTool(manager)
        
        assert tool.name == "github_get_commit"
        assert "sha" in tool.input_schema["required"]


# Branch Tests
class TestListBranchesTool:
    """Tests for ListBranchesTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListBranchesTool(manager)
        
        assert tool.name == "github_list_branches"
        assert "branch" in tool.description.lower()


class TestCreateBranchTool:
    """Tests for CreateBranchTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CreateBranchTool(manager)
        
        assert tool.name == "github_create_branch"
        assert "branch" in tool.input_schema["required"]


class TestCompareBranchesTool:
    """Tests for CompareBranchesTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CompareBranchesTool(manager)
        
        assert tool.name == "github_compare_branches"
        assert "base" in tool.input_schema["required"]
        assert "head" in tool.input_schema["required"]


# Release Tests
class TestListReleasesTool:
    """Tests for ListReleasesTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListReleasesTool(manager)
        
        assert tool.name == "github_list_releases"
        assert "release" in tool.description.lower()


class TestCreateReleaseTool:
    """Tests for CreateReleaseTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CreateReleaseTool(manager)
        
        assert tool.name == "github_create_release"
        assert "tag_name" in tool.input_schema["required"]


class TestListTagsTool:
    """Tests for ListTagsTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListTagsTool(manager)
        
        assert tool.name == "github_list_tags"
        assert "tag" in tool.description.lower()


# Actions Tests
class TestListWorkflowsTool:
    """Tests for ListWorkflowsTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListWorkflowsTool(manager)
        
        assert tool.name == "github_list_workflows"
        assert "workflow" in tool.description.lower()


class TestTriggerWorkflowTool:
    """Tests for TriggerWorkflowTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = TriggerWorkflowTool(manager)
        
        assert tool.name == "github_trigger_workflow"
        assert "workflow_id" in tool.input_schema["required"]


class TestListWorkflowRunsTool:
    """Tests for ListWorkflowRunsTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = ListWorkflowRunsTool(manager)
        
        assert tool.name == "github_list_workflow_runs"
        assert "run" in tool.description.lower()


class TestCancelWorkflowRunTool:
    """Tests for CancelWorkflowRunTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = CancelWorkflowRunTool(manager)
        
        assert tool.name == "github_cancel_workflow_run"
        assert "run_id" in tool.input_schema["required"]


class TestRerunWorkflowTool:
    """Tests for RerunWorkflowTool."""

    def test_tool_properties(self):
        """Test tool name, description, and schema."""
        manager = Mock()
        tool = RerunWorkflowTool(manager)
        
        assert tool.name == "github_rerun_workflow"
        assert "rerun" in tool.description.lower()


# Note: Full integration tests would require actual GitHub API access
# or comprehensive mocking of PyGithub responses
