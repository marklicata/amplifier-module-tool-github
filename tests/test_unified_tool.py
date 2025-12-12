"""Tests for GitHubUnifiedTool."""

import pytest
from unittest.mock import Mock, AsyncMock
from amplifier_module_tool_github.unified_tool import GitHubUnifiedTool
from amplifier_module_tool_github.manager import GitHubManager


class TestGitHubUnifiedTool:
    """Tests for GitHubUnifiedTool class."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock GitHubManager."""
        manager = Mock(spec=GitHubManager)
        manager.is_authenticated.return_value = True
        return manager

    def test_tool_properties(self, mock_manager):
        """Test tool name, description, and schema."""
        tool = GitHubUnifiedTool(mock_manager)
        
        assert tool.name == "github"
        assert "GitHub" in tool.description
        assert "34" in tool.description or "operations" in tool.description
        
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "operation" in schema["properties"]
        assert "parameters" in schema["properties"]
        assert schema["required"] == ["operation", "parameters"]

    def test_all_operations_available(self, mock_manager):
        """Test that all 34 operations are available."""
        tool = GitHubUnifiedTool(mock_manager)
        
        assert len(tool._tools) == 34
        
        # Check some key operations exist
        expected_ops = [
            "list_issues", "get_issue", "create_issue",
            "list_pull_requests", "create_pull_request",
            "get_repository", "list_repositories",
            "list_commits", "get_commit",
            "list_branches", "create_branch",
            "list_releases", "create_release",
            "list_workflows", "trigger_workflow",
        ]
        
        for op in expected_ops:
            assert op in tool._tools

    @pytest.mark.asyncio
    async def test_execute_missing_operation(self, mock_manager):
        """Test executing without operation parameter."""
        tool = GitHubUnifiedTool(mock_manager)
        
        result = await tool.execute({"parameters": {}})
        
        assert not result.success
        assert "operation" in result.error["message"].lower()

    @pytest.mark.asyncio
    async def test_execute_invalid_operation(self, mock_manager):
        """Test executing with invalid operation."""
        tool = GitHubUnifiedTool(mock_manager)
        
        result = await tool.execute({
            "operation": "invalid_operation",
            "parameters": {}
        })
        
        assert not result.success
        assert "unknown operation" in result.error["message"].lower()

    @pytest.mark.asyncio
    async def test_execute_invalid_parameters_type(self, mock_manager):
        """Test executing with non-dict parameters."""
        tool = GitHubUnifiedTool(mock_manager)
        
        result = await tool.execute({
            "operation": "list_issues",
            "parameters": "not a dict"
        })
        
        assert not result.success
        assert "parameters must be an object" in result.error["message"].lower()

    @pytest.mark.asyncio
    async def test_execute_delegates_to_tool(self, mock_manager):
        """Test that execute delegates to the appropriate tool."""
        tool = GitHubUnifiedTool(mock_manager)
        
        # Mock the underlying tool's execute method
        mock_result = Mock()
        mock_result.success = True
        mock_result.output = {"test": "data"}
        
        tool._tools["list_issues"].execute = AsyncMock(return_value=mock_result)
        
        result = await tool.execute({
            "operation": "list_issues",
            "parameters": {"repository": "owner/repo"}
        })
        
        # Verify the tool was called
        tool._tools["list_issues"].execute.assert_called_once_with(
            {"repository": "owner/repo"}
        )
        
        assert result.success
        assert result.output == {"test": "data"}

    def test_get_operation_schema(self, mock_manager):
        """Test getting schema for specific operation."""
        tool = GitHubUnifiedTool(mock_manager)
        
        schema = tool.get_operation_schema("list_issues")
        assert schema is not None
        assert "type" in schema
        
        # Non-existent operation
        schema = tool.get_operation_schema("nonexistent")
        assert schema is None

    def test_list_operations(self, mock_manager):
        """Test listing all operations."""
        tool = GitHubUnifiedTool(mock_manager)
        
        operations = tool.list_operations()
        
        assert len(operations) == 34
        assert all("operation" in op for op in operations)
        assert all("description" in op for op in operations)
        
        # Check operations are sorted
        op_names = [op["operation"] for op in operations]
        assert op_names == sorted(op_names)

    def test_operation_enum_in_schema(self, mock_manager):
        """Test that all operations are in the enum."""
        tool = GitHubUnifiedTool(mock_manager)
        
        schema = tool.input_schema
        enum_values = schema["properties"]["operation"]["enum"]
        
        assert len(enum_values) == 34
        assert "list_issues" in enum_values
        assert "create_pull_request" in enum_values
        assert "trigger_workflow" in enum_values
