"""Create a new issue in a repository."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    RateLimitError,
    PermissionError,
    ValidationError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class CreateIssueTool(GitHubBaseTool):
    """Tool to create a new issue in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_issue"

    @property
    def description(self) -> str:
        return (
            "Create a new issue in a GitHub repository. Requires write access to the repository. "
            "Can set title, body, labels, assignees, and milestone."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "Full repository name in format 'owner/repo' (e.g., 'microsoft/vscode')"
                },
                "title": {
                    "type": "string",
                    "description": "Issue title (required)"
                },
                "body": {
                    "type": "string",
                    "description": "Issue body/description (supports Markdown)"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to add to the issue"
                },
                "assignees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Usernames to assign to the issue"
                },
                "milestone": {
                    "type": "integer",
                    "description": "Milestone number to associate with the issue"
                }
            },
            "required": ["repository", "title"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new issue."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        title = input_data.get("title")
        body = input_data.get("body")
        labels = input_data.get("labels", [])
        assignees = input_data.get("assignees", [])
        milestone_number = input_data.get("milestone")

        if not repository or not title:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and title parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not title.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Issue title cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get milestone object if specified
            milestone = None
            if milestone_number is not None:
                try:
                    milestone = repo.get_milestone(number=milestone_number)
                except Exception:
                    return ToolResult(
                        success=False,
                        error={
                            "message": f"Milestone #{milestone_number} not found",
                            "code": "MILESTONE_NOT_FOUND"
                        }
                    )

            # Create the issue
            issue = repo.create_issue(
                title=title,
                body=body or "",
                labels=labels if labels else None,
                assignees=assignees if assignees else None,
                milestone=milestone,
            )

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "issue": {
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "url": issue.html_url,
                        "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    },
                    "message": f"Issue #{issue.number} created successfully"
                }
            )

        except RepositoryNotFoundError as e:
            return ToolResult(success=False, error=e.to_dict())

        except RateLimitError as e:
            return ToolResult(success=False, error=e.to_dict())

        except GithubException as e:
            # Check for permission errors
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create issue").to_dict()
                )
            return ToolResult(
                success=False,
                error={
                    "message": f"GitHub API error: {str(e)}",
                    "code": "GITHUB_API_ERROR"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Unexpected error: {str(e)}",
                    "code": "UNEXPECTED_ERROR"
                }
            )
