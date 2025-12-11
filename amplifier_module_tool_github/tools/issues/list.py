"""List issues in a repository."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    RateLimitError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class ListIssuesTool(GitHubBaseTool):
    """Tool to list issues in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_issues"

    @property
    def description(self) -> str:
        return (
            "List issues in a GitHub repository. Returns a list of issues with their "
            "basic information including number, title, state, author, labels, and dates. "
            "Supports filtering by state (open/closed/all), labels, assignee, and more."
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
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "Filter by issue state (default: open)",
                    "default": "open"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by labels (must have all specified labels)"
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter by assignee username (use 'none' for unassigned, '*' for any assigned)"
                },
                "creator": {
                    "type": "string",
                    "description": "Filter by issue creator username"
                },
                "mentioned": {
                    "type": "string",
                    "description": "Filter by username mentioned in the issue"
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "comments"],
                    "description": "Sort field (default: created)",
                    "default": "created"
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort direction (default: desc)",
                    "default": "desc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of issues to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List issues in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        state = input_data.get("state", "open")
        labels = input_data.get("labels", [])
        assignee = input_data.get("assignee")
        creator = input_data.get("creator")
        mentioned = input_data.get("mentioned")
        sort = input_data.get("sort", "created")
        direction = input_data.get("direction", "desc")
        limit = input_data.get("limit", 30)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get issues with filters
            issues = repo.get_issues(
                state=state,
                labels=labels if labels else None,
                assignee=assignee if assignee else None,
                creator=creator if creator else None,
                mentioned=mentioned if mentioned else None,
                sort=sort,
                direction=direction,
            )

            # Collect issue data
            issue_list = []
            count = 0
            for issue in issues:
                if count >= limit:
                    break
                
                # Skip pull requests (GitHub's API returns PRs as issues)
                if issue.pull_request:
                    continue

                issue_data = {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "author": issue.user.login if issue.user else None,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "comments": issue.comments,
                    "url": issue.html_url,
                }
                issue_list.append(issue_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "state": state,
                    "count": len(issue_list),
                    "issues": issue_list,
                }
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
