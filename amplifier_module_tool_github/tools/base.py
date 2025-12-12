"""Base class for GitHub tools."""

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import GitHubManager

from ..exceptions import AuthenticationError, PermissionError

try:
    from amplifier_core import ToolResult
except ImportError:
    # Fallback for testing without amplifier-core
    class ToolResult:
        def __init__(self, success: bool, output: dict | None = None, error: dict | None = None):
            self.success = success
            self.output = output or {}
            self.error = error or {}

logger = logging.getLogger(__name__)


class GitHubBaseTool:
    """Base class for all GitHub tools."""

    def __init__(self, manager: "GitHubManager"):
        """
        Initialize the tool.

        Args:
            manager: The GitHubManager instance
        """
        self.manager = manager

    @property
    def name(self) -> str:
        """Tool name - must be implemented by subclasses."""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """Tool description - must be implemented by subclasses."""
        raise NotImplementedError

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON schema for tool input - must be implemented by subclasses."""
        raise NotImplementedError

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """
        Execute the tool - must be implemented by subclasses.

        Args:
            input_data: Input parameters matching the input_schema

        Returns:
            ToolResult with success status and output/error data
        """
        raise NotImplementedError

    def _check_authentication(self) -> ToolResult | None:
        """
        Check if GitHub client is authenticated.

        Returns:
            ToolResult with error if not authenticated, None otherwise
        """
        if not self.manager.is_authenticated():
            error = AuthenticationError()
            return ToolResult(
                success=False,
                error=error.to_dict()
            )
        return None

    def _require_authentication(self) -> None:
        """
        Ensure GitHub client is authenticated.

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.manager.is_authenticated():
            raise AuthenticationError()
    
    def _check_repository_access(self, repository: str) -> ToolResult | None:
        """
        Check if access to a repository is allowed based on configuration.

        Args:
            repository: Repository name in owner/repo format

        Returns:
            ToolResult with error if not allowed, None otherwise
        """
        if not self.manager.is_repository_allowed(repository):
            configured = self.manager.get_configured_repositories()
            error = PermissionError(
                f"Access to repository '{repository}' is not allowed. "
                f"Configured repositories: {', '.join(configured)}"
            )
            return ToolResult(
                success=False,
                error=error.to_dict()
            )
        return None
