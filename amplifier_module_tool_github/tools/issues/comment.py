"""Add a comment to an issue."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    IssueNotFoundError,
    RateLimitError,
    PermissionError,
    ValidationError,
    GitHubError,
)

try:
    from github.GithubException import GithubException, UnknownObjectException
except ImportError:
    GithubException = Exception
    UnknownObjectException = Exception


class CommentIssueTool(GitHubBaseTool):
    """Tool to add a comment to an issue."""

    @property
    def name(self) -> str:
        return "github_comment_issue"

    @property
    def description(self) -> str:
        return (
            "Add a comment to a GitHub issue. Requires write access to the repository. "
            "The comment body supports Markdown formatting."
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
                "issue_number": {
                    "type": "integer",
                    "description": "Issue number"
                },
                "body": {
                    "type": "string",
                    "description": "Comment body/text (supports Markdown)"
                }
            },
            "required": ["repository", "issue_number", "body"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Add a comment to an issue."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        issue_number = input_data.get("issue_number")
        body = input_data.get("body")

        if not repository or issue_number is None or not body:
            return ToolResult(
                success=False,
                error={
                    "message": "repository, issue_number, and body parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not body.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Comment body cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)
            issue = repo.get_issue(number=issue_number)

            # Check if it's actually a pull request
            if issue.pull_request:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"#{issue_number} is a pull request, not an issue. Use pull request tools instead.",
                        "code": "NOT_AN_ISSUE"
                    }
                )

            # Add the comment
            comment = issue.create_comment(body=body)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "issue_number": issue_number,
                    "comment": {
                        "id": comment.id,
                        "body": comment.body,
                        "author": comment.user.login if comment.user else None,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "url": comment.html_url,
                    },
                    "message": "Comment added successfully"
                }
            )

        except UnknownObjectException:
            return ToolResult(
                success=False,
                error=IssueNotFoundError(issue_number, repository).to_dict()
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
                    error=PermissionError("comment on issue").to_dict()
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
