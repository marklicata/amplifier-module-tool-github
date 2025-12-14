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
            return ToolResult(
                success=False,
                error={
                    "message": f"Access to repository '{repository}' is not allowed. "
                              f"Configured repositories: {', '.join(configured)}",
                    "code": "PERMISSION_DENIED"
                }
            )
        return None
    
    def _resolve_username(self, username: str | None) -> tuple[str | None, ToolResult | None]:
        """
        Resolve a username, translating @me to the authenticated user's username.
        
        NOTE: @me resolution is now handled centrally in unified_tool.py's execute() method
        before parameters reach individual tools. These helpers are kept as fallbacks for
        edge cases or direct tool invocation, but normal operation doesn't require calling them.
        
        Args:
            username: Username string, which may be "@me", an actual username, or None
        
        Returns:
            Tuple of (resolved_username, error_result)
            - If successful: (resolved_username, None)
            - If error: (None, ToolResult with error)
        """
        if username == "@me":
            try:
                user = self.manager.client.get_user()
                return (user.login, None)
            except Exception as e:
                error_msg = str(e) if str(e) else repr(e)
                return (None, ToolResult(
                    success=False,
                    error={
                        "message": f"Failed to resolve @me to authenticated user: {error_msg}",
                        "code": "AUTHENTICATION_ERROR",
                        "type": type(e).__name__
                    }
                ))
        return (username, None)
    
    def _resolve_usernames(self, usernames: list[str] | None) -> tuple[list[str] | None, ToolResult | None]:
        """
        Resolve a list of usernames, translating any @me to the authenticated user's username.
        
        NOTE: @me resolution is now handled centrally in unified_tool.py's execute() method
        before parameters reach individual tools. This helper is kept as a fallback.
        
        Args:
            usernames: List of username strings, which may include "@me"
        
        Returns:
            Tuple of (resolved_usernames, error_result)
            - If successful: (resolved_usernames, None)
            - If error: (None, ToolResult with error)
        """
        if not usernames:
            return (usernames, None)
        
        resolved = []
        for username in usernames:
            resolved_username, error = self._resolve_username(username)
            if error:
                return (None, error)
            if resolved_username:
                resolved.append(resolved_username)
        
        return (resolved, None)
