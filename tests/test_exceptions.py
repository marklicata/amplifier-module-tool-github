"""Tests for GitHub exceptions."""

import pytest
from amplifier_module_tool_github.exceptions import (
    GitHubError,
    AuthenticationError,
    RepositoryNotFoundError,
    IssueNotFoundError,
    RateLimitError,
    PermissionError,
    ValidationError,
    ToolExecutionError,
)


def test_github_error():
    """Test base GitHubError exception."""
    error = GitHubError("Test error", "TEST_CODE")
    assert str(error) == "Test error"
    assert error.code == "TEST_CODE"
    assert error.to_dict() == {
        "message": "Test error",
        "code": "TEST_CODE"
    }


def test_authentication_error():
    """Test AuthenticationError exception."""
    error = AuthenticationError()
    assert "authentication" in str(error).lower()
    assert error.code == "AUTHENTICATION_ERROR"


def test_repository_not_found_error():
    """Test RepositoryNotFoundError exception."""
    error = RepositoryNotFoundError("owner/repo")
    assert "owner/repo" in str(error)
    assert error.code == "REPOSITORY_NOT_FOUND"


def test_issue_not_found_error():
    """Test IssueNotFoundError exception."""
    error = IssueNotFoundError(123, "owner/repo")
    assert "123" in str(error)
    assert "owner/repo" in str(error)
    assert error.code == "ISSUE_NOT_FOUND"


def test_rate_limit_error():
    """Test RateLimitError exception."""
    error = RateLimitError("2024-01-01T00:00:00Z")
    assert "rate limit" in str(error).lower()
    assert "2024-01-01T00:00:00Z" in str(error)
    assert error.code == "RATE_LIMIT_EXCEEDED"


def test_permission_error():
    """Test PermissionError exception."""
    error = PermissionError("create issue")
    assert "create issue" in str(error)
    assert error.code == "PERMISSION_DENIED"


def test_validation_error():
    """Test ValidationError exception."""
    error = ValidationError("Invalid input")
    assert "Invalid input" in str(error)
    assert error.code == "VALIDATION_ERROR"


def test_tool_execution_error():
    """Test ToolExecutionError exception."""
    error = ToolExecutionError("test_tool", "Something went wrong")
    assert "test_tool" in str(error)
    assert "Something went wrong" in str(error)
    assert error.code == "TOOL_EXECUTION_ERROR"
