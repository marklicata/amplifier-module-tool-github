"""Unified GitHub tool that consolidates all operations."""

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import GitHubManager

from .exceptions import ValidationError, ToolExecutionError

# Import all tool implementations
from .tools import (
    # Issues
    ListIssuesTool, GetIssueTool, CreateIssueTool, UpdateIssueTool, CommentIssueTool,
    # Pull Requests
    ListPullRequestsTool, GetPullRequestTool, CreatePullRequestTool,
    UpdatePullRequestTool, MergePullRequestTool, ReviewPullRequestTool,
    # Repositories
    GetRepositoryTool, ListRepositoriesTool, CreateRepositoryTool,
    GetFileContentTool, ListRepositoryContentsTool,
    # Commits
    ListCommitsTool, GetCommitTool,
    # Branches
    ListBranchesTool, GetBranchTool, CreateBranchTool, CompareBranchesTool,
    # Releases
    ListReleasesTool, GetReleaseTool, CreateReleaseTool, ListTagsTool, CreateTagTool,
    # Actions
    ListWorkflowsTool, GetWorkflowTool, TriggerWorkflowTool,
    ListWorkflowRunsTool, GetWorkflowRunTool, CancelWorkflowRunTool, RerunWorkflowTool,
)

try:
    from amplifier_core import ToolResult
except ImportError:
    class ToolResult:
        def __init__(self, success: bool, output: dict | None = None, error: dict | None = None):
            self.success = success
            self.output = output or {}
            self.error = error or {}

logger = logging.getLogger(__name__)


class GitHubUnifiedTool:
    """
    Unified GitHub tool that provides access to all GitHub operations.
    
    This tool acts as a single entry point for all GitHub API interactions,
    with the specific operation determined by the 'operation' parameter.
    """

    def __init__(self, manager: "GitHubManager"):
        """Initialize the unified tool with a GitHub manager."""
        self.manager = manager
        
        # Initialize all individual tool instances
        self._tools = {
            # Issues
            "list_issues": ListIssuesTool(manager),
            "get_issue": GetIssueTool(manager),
            "create_issue": CreateIssueTool(manager),
            "update_issue": UpdateIssueTool(manager),
            "comment_issue": CommentIssueTool(manager),
            # Pull Requests
            "list_pull_requests": ListPullRequestsTool(manager),
            "get_pull_request": GetPullRequestTool(manager),
            "create_pull_request": CreatePullRequestTool(manager),
            "update_pull_request": UpdatePullRequestTool(manager),
            "merge_pull_request": MergePullRequestTool(manager),
            "review_pull_request": ReviewPullRequestTool(manager),
            # Repositories
            "get_repository": GetRepositoryTool(manager),
            "list_repositories": ListRepositoriesTool(manager),
            "create_repository": CreateRepositoryTool(manager),
            "get_file_content": GetFileContentTool(manager),
            "list_repository_contents": ListRepositoryContentsTool(manager),
            # Commits
            "list_commits": ListCommitsTool(manager),
            "get_commit": GetCommitTool(manager),
            # Branches
            "list_branches": ListBranchesTool(manager),
            "get_branch": GetBranchTool(manager),
            "create_branch": CreateBranchTool(manager),
            "compare_branches": CompareBranchesTool(manager),
            # Releases
            "list_releases": ListReleasesTool(manager),
            "get_release": GetReleaseTool(manager),
            "create_release": CreateReleaseTool(manager),
            "list_tags": ListTagsTool(manager),
            "create_tag": CreateTagTool(manager),
            # Actions
            "list_workflows": ListWorkflowsTool(manager),
            "get_workflow": GetWorkflowTool(manager),
            "trigger_workflow": TriggerWorkflowTool(manager),
            "list_workflow_runs": ListWorkflowRunsTool(manager),
            "get_workflow_run": GetWorkflowRunTool(manager),
            "cancel_workflow_run": CancelWorkflowRunTool(manager),
            "rerun_workflow": RerunWorkflowTool(manager),
        }

    @property
    def name(self) -> str:
        """Tool name."""
        return "github"

    @property
    def description(self) -> str:
        """Tool description."""
        return (
            "Interact with GitHub repositories and resources. When repositories are configured in settings, "
            "many operations can query across ALL configured repos automatically. Otherwise, specify a repository "
            "parameter to target a specific repo. Supports 34 operations for issues, PRs, commits, branches, "
            "workflows, releases, and more.\n\n"
            "Cross-Repository Queries (when repositories configured):\n"
            "- list_issues: Find issues across all your configured repos (filter by assignee, creator, labels)\n"
            "- list_pull_requests: Find PRs across all your repos (filter by state, author)\n\n"
            "Repository-Specific Operations:\n"
            "- All operations work on a specific repository when 'repository' parameter is provided\n"
            "- Examples: get_commit, create_branch, trigger_workflow, merge_pull_request\n\n"
            "User-Level Operations:\n"
            "- list_repositories: List repos for a user/org\n"
            "- create_repository: Create a new repo"
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON schema for tool input."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The GitHub operation to perform",
                    "enum": list(self._tools.keys()),
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the specific operation (schema varies by operation)",
                    "additionalProperties": True,
                },
            },
            "required": ["operation", "parameters"],
            "additionalProperties": False,
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """
        Execute a GitHub operation.

        Args:
            input_data: Input with 'operation' and 'parameters' keys

        Returns:
            ToolResult with success status and output/error data
        """
        try:
            # Validate input
            operation = input_data.get("operation")
            if not operation:
                error = ValidationError("Missing required field: operation")
                return ToolResult(success=False, error=error.to_dict())

            parameters = input_data.get("parameters", {})
            if not isinstance(parameters, dict):
                error = ValidationError("parameters must be an object")
                return ToolResult(success=False, error=error.to_dict())

            # Get the specific tool
            tool = self._tools.get(operation)
            if not tool:
                available = ", ".join(sorted(self._tools.keys()))
                error = ValidationError(
                    f"Unknown operation: {operation}. Available operations: {available}"
                )
                return ToolResult(success=False, error=error.to_dict())

            # Execute the specific tool
            logger.debug(f"Executing GitHub operation: {operation}")
            result = await tool.execute(parameters)
            
            return result

        except Exception as e:
            logger.error(f"Unexpected error in GitHub tool: {e}")
            error = ToolExecutionError(f"Unexpected error: {str(e)}")
            return ToolResult(success=False, error=error.to_dict())

    def get_operation_schema(self, operation: str) -> dict[str, Any] | None:
        """
        Get the input schema for a specific operation.

        Args:
            operation: The operation name

        Returns:
            Input schema dict or None if operation doesn't exist
        """
        tool = self._tools.get(operation)
        if tool:
            return tool.input_schema
        return None

    def list_operations(self) -> list[dict[str, str]]:
        """
        List all available operations with their descriptions.

        Returns:
            List of dicts with 'operation' and 'description' keys
        """
        operations = []
        for op_name, tool in sorted(self._tools.items()):
            operations.append({
                "operation": op_name,
                "description": tool.description,
            })
        return operations
