"""Tests for GitHub tools."""

import pytest
from unittest.mock import Mock, AsyncMock
from amplifier_module_tool_github.tools import (
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
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


# Note: Full integration tests would require actual GitHub API access
# or comprehensive mocking of PyGithub responses
