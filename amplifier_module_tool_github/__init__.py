"""
GitHub Integration Module for Amplifier

This module provides GitHub API integration capabilities as tools for Amplifier LLM agents.
It enables interaction with GitHub repositories, issues, pull requests, and other GitHub features.

Implementation Status: Version 1.5.0
- ✅ Issues: Full CRUD operations and commenting (5 tools)
- ✅ Pull Requests: Create, review, merge PRs (6 tools)
- ✅ Repositories: Browse, create, manage repos (5 tools)
- ✅ Commits: View commit history and details (2 tools)
- ✅ Branches: List, create, compare branches (4 tools)
- ✅ Releases & Tags: Manage releases and tags (5 tools)
- ✅ Actions/Workflows: Trigger and monitor workflows (7 tools)

Total: 34 tools implemented

Future Features:
- 🔲 Projects: Manage GitHub Projects
- 🔲 Code Search: Search across repositories
- 🔲 Security: Dependabot alerts, security advisories
- 🔲 Advanced Repository: Webhooks, deploy keys, collaborators
- 🔲 Discussions: Create and manage discussions
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

__version__ = "1.5.0"

logger = logging.getLogger(__name__)


async def mount(coordinator: "ModuleCoordinator", config: dict[str, Any] | None = None):
    """
    Mount the GitHub module with Amplifier.

    This function is the entry point called by Amplifier to initialize and
    register the GitHub tools.

    Args:
        coordinator: The ModuleCoordinator instance for registering capabilities
        config: Optional configuration dictionary with settings:
            - token: GitHub personal access token or GitHub App token (optional)
            - use_cli_auth: Use GitHub CLI authentication if token not provided (default: True)
            - prompt_if_missing: Prompt user for token if no auth found (default: True)
            - base_url: GitHub Enterprise URL (optional, defaults to github.com)
    
    Authentication is attempted in this order:
        1. Explicit token in config
        2. GITHUB_TOKEN or GH_TOKEN environment variable
        3. GitHub CLI (gh auth token) if use_cli_auth is True
        4. Interactive prompt if prompt_if_missing is True

    Returns:
        Async cleanup function to be called when the module is unmounted
    """
    config = config or {}

    logger.info("Mounting GitHub module...")

    try:
        # Initialize the manager
        manager = GitHubManager(config)
        await manager.start()

        # Create all tool instances (34 tools)
        tools = [
            # Issues (5 tools)
            ListIssuesTool(manager),
            GetIssueTool(manager),
            CreateIssueTool(manager),
            UpdateIssueTool(manager),
            CommentIssueTool(manager),
            # Pull Requests (6 tools)
            ListPullRequestsTool(manager),
            GetPullRequestTool(manager),
            CreatePullRequestTool(manager),
            UpdatePullRequestTool(manager),
            MergePullRequestTool(manager),
            ReviewPullRequestTool(manager),
            # Repositories (5 tools)
            GetRepositoryTool(manager),
            ListRepositoriesTool(manager),
            CreateRepositoryTool(manager),
            GetFileContentTool(manager),
            ListRepositoryContentsTool(manager),
            # Commits (2 tools)
            ListCommitsTool(manager),
            GetCommitTool(manager),
            # Branches (4 tools)
            ListBranchesTool(manager),
            GetBranchTool(manager),
            CreateBranchTool(manager),
            CompareBranchesTool(manager),
            # Releases (5 tools)
            ListReleasesTool(manager),
            GetReleaseTool(manager),
            CreateReleaseTool(manager),
            ListTagsTool(manager),
            CreateTagTool(manager),
            # Actions (7 tools)
            ListWorkflowsTool(manager),
            GetWorkflowTool(manager),
            TriggerWorkflowTool(manager),
            ListWorkflowRunsTool(manager),
            GetWorkflowRunTool(manager),
            CancelWorkflowRunTool(manager),
            RerunWorkflowTool(manager),
        ]

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
