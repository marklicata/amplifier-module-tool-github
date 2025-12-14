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
            "IMPORTANT - Username Parameters:\n"
            "- When filtering by username (assignee, creator, mentioned, etc.), use the actual GitHub username\n"
            "- Example: Use 'octocat' NOT '@octocat'\n"
            "- Special value '@me' is not supported. It should be the authenticated username\n"
            "- To get the authenticated user's username, first call get_user operation\n\n"
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

    def _resolve_username_in_parameters(self, parameters: dict[str, Any]) -> tuple[dict[str, Any], ToolResult | None]:
        """
        Recursively resolve @me to authenticated username in all username parameters.
        
        This is the central location where @me translation happens for ALL operations.
        Individual tools don't need to handle this - it's done here at the entry point.
        
        Username parameters that support @me:
        - assignee (string)
        - assignees (array of strings)
        - creator (string)
        - mentioned (string)
        - author (string)
        - reviewers (array of strings)
        - add_reviewers (array of strings)
        - remove_reviewers (array of strings)
        
        Args:
            parameters: Parameters dict from the operation call
        
        Returns:
            Tuple of (resolved_parameters, error_result)
            - If successful: (resolved_parameters, None)
            - If error: (original_parameters, ToolResult with error)
        """
        # Username parameter names that support @me translation
        STRING_USERNAME_PARAMS = {"assignee", "creator", "mentioned", "author"}
        ARRAY_USERNAME_PARAMS = {"assignees", "reviewers", "add_reviewers", "remove_reviewers"}
        
        resolved_params = parameters.copy()
        
        # Get authenticated user once if needed
        authenticated_username = None
        needs_resolution = any(
            (param in parameters and parameters[param] == "@me") 
            for param in STRING_USERNAME_PARAMS
        ) or any(
            (param in parameters and isinstance(parameters[param], list) and "@me" in parameters[param])
            for param in ARRAY_USERNAME_PARAMS
        )
        
        if needs_resolution:
            try:
                user = self.manager.client.get_user()
                authenticated_username = user.login
                logger.debug(f"Resolved @me to {authenticated_username}")
            except Exception as e:
                error_msg = str(e) if str(e) else repr(e)
                return (parameters, ToolResult(
                    success=False,
                    error={
                        "message": f"Failed to resolve @me to authenticated user: {error_msg}",
                        "code": "AUTHENTICATION_ERROR",
                        "type": type(e).__name__
                    }
                ))
        
        # Resolve string username parameters
        for param in STRING_USERNAME_PARAMS:
            if param in resolved_params and resolved_params[param] == "@me":
                resolved_params[param] = authenticated_username
                logger.debug(f"Resolved {param}=@me to {authenticated_username}")
        
        # Resolve array username parameters
        for param in ARRAY_USERNAME_PARAMS:
            if param in resolved_params and isinstance(resolved_params[param], list):
                original_list = resolved_params[param]
                if "@me" in original_list:
                    resolved_list = [
                        authenticated_username if username == "@me" else username
                        for username in original_list
                    ]
                    resolved_params[param] = resolved_list
                    logger.debug(f"Resolved {param} array containing @me to {resolved_list}")
        
        return (resolved_params, None)

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

            # Resolve @me in all username parameters BEFORE passing to individual tools
            # This is the single point where @me translation happens for ALL operations
            parameters, error = self._resolve_username_in_parameters(parameters)
            if error:
                return error

            # Get the specific tool
            tool = self._tools.get(operation)
            if not tool:
                available = ", ".join(sorted(self._tools.keys()))
                error = ValidationError(
                    f"Unknown operation: {operation}. Available operations: {available}"
                )
                return ToolResult(success=False, error=error.to_dict())

            # Execute the specific tool with resolved parameters
            logger.debug(f"Executing GitHub operation: {operation}")
            result = await tool.execute(parameters)
            
            return result

        except Exception as e:
            logger.error(f"Unexpected error in GitHub tool: {e}")
            error = ToolExecutionError("github", f"Unexpected error: {str(e)}")
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
