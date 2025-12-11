"""
GitHub Integration Module for Amplifier

This module provides GitHub API integration capabilities as tools for Amplifier LLM agents.
It enables interaction with GitHub repositories, issues, pull requests, and other GitHub features.

V1 Implementation Status:
- ✓ Issues: Full CRUD operations and commenting
- TODO: Pull Requests
- TODO: Repositories  
- TODO: Commits
- TODO: Branches
- TODO: Releases
- TODO: Actions/Workflows
- TODO: Projects
- TODO: Code Search
- TODO: Security/Dependabot

Tools provided (V1):
- github_list_issues: List issues in a repository
- github_get_issue: Get detailed information about an issue
- github_create_issue: Create a new issue
- github_update_issue: Update an existing issue
- github_comment_issue: Add a comment to an issue
"""

import logging
from typing import Any

try:
    from amplifier_core import ModuleCoordinator
except ImportError:
    ModuleCoordinator = None

from .manager import GitHubManager
from .exceptions import (
    GitHubError,
    AuthenticationError,
    RepositoryNotFoundError,
    IssueNotFoundError,
    RateLimitError,
    PermissionError,
    ValidationError,
    ToolExecutionError,
)
from .tools import (
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
)

__version__ = "0.1.0"

logger = logging.getLogger(__name__)


async def mount(coordinator: "ModuleCoordinator", config: dict[str, Any] | None = None):
    """
    Mount the GitHub module with Amplifier.

    This function is the entry point called by Amplifier to initialize and
    register the GitHub tools.

    Args:
        coordinator: The ModuleCoordinator instance for registering capabilities
        config: Optional configuration dictionary with settings:
            - token: GitHub personal access token or GitHub App token (required)
            - base_url: GitHub Enterprise URL (optional, defaults to github.com)

    Returns:
        Async cleanup function to be called when the module is unmounted
    """
    config = config or {}

    logger.info("Mounting GitHub module...")

    try:
        # Initialize the manager
        manager = GitHubManager(config)
        await manager.start()

        # Create tool instances - V1: Issues only
        tools = [
            ListIssuesTool(manager),
            GetIssueTool(manager),
            CreateIssueTool(manager),
            UpdateIssueTool(manager),
            CommentIssueTool(manager),
        ]

        # TODO: Add more tools in future versions:
        # Pull Requests:
        #   - ListPullRequestsTool(manager)
        #   - GetPullRequestTool(manager)
        #   - CreatePullRequestTool(manager)
        #   - UpdatePullRequestTool(manager)
        #   - MergePullRequestTool(manager)
        #   - ReviewPullRequestTool(manager)
        #
        # Repositories:
        #   - GetRepositoryTool(manager)
        #   - ListRepositoriesTool(manager)
        #   - CreateRepositoryTool(manager)
        #
        # Commits:
        #   - ListCommitsTool(manager)
        #   - GetCommitTool(manager)
        #
        # Branches:
        #   - ListBranchesTool(manager)
        #   - GetBranchTool(manager)
        #   - CreateBranchTool(manager)
        #
        # Releases:
        #   - ListReleasesTool(manager)
        #   - GetReleaseTool(manager)
        #   - CreateReleaseTool(manager)
        #
        # Actions:
        #   - ListWorkflowsTool(manager)
        #   - TriggerWorkflowTool(manager)
        #   - GetWorkflowRunTool(manager)
        #
        # Projects:
        #   - ListProjectsTool(manager)
        #   - GetProjectTool(manager)
        #
        # Code:
        #   - SearchCodeTool(manager)
        #   - GetFileContentTool(manager)
        #
        # Security:
        #   - ListDependabotAlertsTool(manager)
        #   - ListSecurityAdvisoriesTool(manager)

        # Register each tool with the coordinator
        for tool in tools:
            await coordinator.mount("tools", tool, name=tool.name)
            logger.debug(f"Mounted GitHub tool: {tool.name}")

        logger.info(f"GitHub module mounted successfully with {len(tools)} tools")

        # Return cleanup function
        async def cleanup():
            logger.info("Cleaning up GitHub module...")
            await manager.stop()

        return cleanup

    except Exception as e:
        logger.error(f"Failed to mount GitHub module: {e}")
        raise


__all__ = [
    "mount",
    "GitHubManager",
    # Exceptions
    "GitHubError",
    "AuthenticationError",
    "RepositoryNotFoundError",
    "IssueNotFoundError",
    "RateLimitError",
    "PermissionError",
    "ValidationError",
    "ToolExecutionError",
    # Tools
    "ListIssuesTool",
    "GetIssueTool",
    "CreateIssueTool",
    "UpdateIssueTool",
    "CommentIssueTool",
]
