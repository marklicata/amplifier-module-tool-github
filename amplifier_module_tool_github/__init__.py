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
from .unified_tool import GitHubUnifiedTool
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
            - repositories: List of repository URLs to restrict access to (optional, default: allow all)
    
    Authentication is attempted in this order:
        1. Explicit token in config
        2. GITHUB_TOKEN or GH_TOKEN environment variable
        3. GitHub CLI (gh auth token) if use_cli_auth is True
        4. Interactive prompt if prompt_if_missing is True
    
    Repository access control:
        - If repositories list is provided, only those repositories can be accessed
        - Supports HTTPS URLs, SSH URLs, and owner/repo format
        - Leave empty to allow access to all repositories (default)

    Returns:
        Async cleanup function to be called when the module is unmounted
    """
    config = config or {}

    logger.info("Mounting GitHub module...")
    logger.debug(f"Config received: {config}")
    logger.debug(f"Repositories in config: {config.get('repositories', [])}")

    try:
        # Initialize the manager
        manager = GitHubManager(config)
        await manager.start()

        # Create the unified GitHub tool (provides 34 operations via single tool)
        github_tool = GitHubUnifiedTool(manager)

        # Register the unified tool
        await coordinator.mount("tools", github_tool, name=github_tool.name)
        logger.info(f"GitHub tool mounted successfully with {len(github_tool._tools)} operations")

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
    "GitHubUnifiedTool",
    # Exceptions
    "GitHubError",
    "AuthenticationError",
    "RepositoryNotFoundError",
    "IssueNotFoundError",
    "RateLimitError",
    "PermissionError",
    "ValidationError",
    "ToolExecutionError",
]