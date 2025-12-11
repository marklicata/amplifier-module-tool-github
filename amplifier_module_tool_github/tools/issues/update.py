"""Update an existing issue."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    IssueNotFoundError,
    RateLimitError,
    PermissionError,
    GitHubError,
)

try:
    from github.GithubException import GithubException, UnknownObjectException
except ImportError:
    GithubException = Exception
    UnknownObjectException = Exception


class UpdateIssueTool(GitHubBaseTool):
    """Tool to update an existing issue."""

    @property
    def name(self) -> str:
        return "github_update_issue"

    @property
    def description(self) -> str:
        return (
            "Update an existing GitHub issue. Requires write access to the repository. "
            "Can update title, body, state, labels, assignees, and milestone. "
            "Only include fields you want to change."
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
                "title": {
                    "type": "string",
                    "description": "New issue title"
                },
                "body": {
                    "type": "string",
                    "description": "New issue body/description (supports Markdown)"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed"],
                    "description": "New issue state"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to set on the issue (replaces existing labels)"
                },
                "assignees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Usernames to assign to the issue (replaces existing assignees)"
                },
                "milestone": {
                    "type": "integer",
                    "description": "Milestone number to associate with the issue (use 0 to remove milestone)"
                }
            },
            "required": ["repository", "issue_number"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Update an issue."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        issue_number = input_data.get("issue_number")
        title = input_data.get("title")
        body = input_data.get("body")
        state = input_data.get("state")
        labels = input_data.get("labels")
        assignees = input_data.get("assignees")
        milestone_number = input_data.get("milestone")

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

            # Build edit parameters (only include what's being changed)
            edit_params = {}
            
            if title is not None:
                edit_params["title"] = title
            
            if body is not None:
                edit_params["body"] = body
            
            if state is not None:
                edit_params["state"] = state
            
            if labels is not None:
                edit_params["labels"] = labels
            
            if assignees is not None:
                edit_params["assignees"] = assignees
            
            if milestone_number is not None:
                if milestone_number == 0:
                    # Remove milestone
                    edit_params["milestone"] = None
                else:
                    try:
                        milestone = repo.get_milestone(number=milestone_number)
                        edit_params["milestone"] = milestone
                    except Exception:
                        return ToolResult(
                            success=False,
                            error={
                                "message": f"Milestone #{milestone_number} not found",
                                "code": "MILESTONE_NOT_FOUND"
                            }
                        )

            # Update the issue
            issue.edit(**edit_params)

            # Refresh to get updated data
            issue = repo.get_issue(number=issue_number)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "issue": {
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "url": issue.html_url,
                        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    },
                    "message": f"Issue #{issue.number} updated successfully"
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
                    error=PermissionError("update issue").to_dict()
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
