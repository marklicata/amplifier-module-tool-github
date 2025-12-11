"""
GitHub Module Exceptions

Custom exception classes for GitHub tool operations.
"""


class GitHubError(Exception):
    """Base exception for all GitHub-related errors."""

    def __init__(self, message: str, code: str = "GITHUB_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for ToolResult."""
        return {
            "message": self.message,
            "code": self.code,
        }


class AuthenticationError(GitHubError):
    """Raised when GitHub authentication fails."""

    def __init__(self, message: str = "GitHub authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class RepositoryNotFoundError(GitHubError):
    """Raised when a repository is not found or not accessible."""

    def __init__(self, repository: str):
        super().__init__(
            f"Repository not found or not accessible: {repository}",
            code="REPOSITORY_NOT_FOUND"
        )


class IssueNotFoundError(GitHubError):
    """Raised when an issue is not found."""

    def __init__(self, issue_number: int, repository: str):
        super().__init__(
            f"Issue #{issue_number} not found in repository {repository}",
            code="ISSUE_NOT_FOUND"
        )


class RateLimitError(GitHubError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, reset_time: str = "unknown"):
        super().__init__(
            f"GitHub API rate limit exceeded. Resets at: {reset_time}",
            code="RATE_LIMIT_EXCEEDED"
        )


class PermissionError(GitHubError):
    """Raised when operation requires permissions not available."""

    def __init__(self, operation: str):
        super().__init__(
            f"Insufficient permissions for operation: {operation}",
            code="PERMISSION_DENIED"
        )


class ValidationError(GitHubError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class ToolExecutionError(GitHubError):
    """Raised when a tool execution fails unexpectedly."""

    def __init__(self, tool_name: str, message: str):
        super().__init__(
            f"Tool '{tool_name}' execution failed: {message}",
            code="TOOL_EXECUTION_ERROR"
        )
