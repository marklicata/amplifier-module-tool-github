"""Get details of a specific issue."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    IssueNotFoundError,
    RateLimitError,
    GitHubError,
)

try:
    from github.GithubException import GithubException, UnknownObjectException
except ImportError:
    GithubException = Exception
    UnknownObjectException = Exception


class GetIssueTool(GitHubBaseTool):
    """Tool to get details of a specific issue."""

    @property
    def name(self) -> str:
        return "github_get_issue"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific GitHub issue including title, "
            "body, state, labels, assignees, comments count, and metadata. "
            "Useful for examining individual issues in detail."
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
                "include_comments": {
                    "type": "boolean",
                    "description": "Include issue comments in the response (default: false)",
                    "default": False
                },
                "comments_limit": {
                    "type": "integer",
                    "description": "Maximum number of comments to return if include_comments is true (default: 10)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository", "issue_number"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get issue details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        issue_number = input_data.get("issue_number")
        include_comments = input_data.get("include_comments", False)
        comments_limit = input_data.get("comments_limit", 10)

        if not repository or issue_number is None:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and issue_number parameters are required",
                    "code": "MISSING_PARAMETER"
                }
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

            issue_data = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "author": {
                    "login": issue.user.login,
                    "url": issue.user.html_url,
                } if issue.user else None,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                "closed_by": {
                    "login": issue.closed_by.login,
                    "url": issue.closed_by.html_url,
                } if issue.closed_by else None,
                "labels": [
                    {"name": label.name, "color": label.color, "description": label.description}
                    for label in issue.labels
                ],
                "assignees": [
                    {"login": assignee.login, "url": assignee.html_url}
                    for assignee in issue.assignees
                ],
                "milestone": {
                    "title": issue.milestone.title,
                    "state": issue.milestone.state,
                    "due_on": issue.milestone.due_on.isoformat() if issue.milestone.due_on else None,
                } if issue.milestone else None,
                "comments_count": issue.comments,
                "locked": issue.locked,
                "url": issue.html_url,
                "api_url": issue.url,
            }

            # Include comments if requested
            if include_comments and issue.comments > 0:
                comments = issue.get_comments()
                comment_list = []
                count = 0
                for comment in comments:
                    if count >= comments_limit:
                        break
                    comment_data = {
                        "id": comment.id,
                        "author": comment.user.login if comment.user else None,
                        "body": comment.body,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
                        "url": comment.html_url,
                    }
                    comment_list.append(comment_data)
                    count += 1
                issue_data["comments"] = comment_list

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "issue": issue_data,
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
