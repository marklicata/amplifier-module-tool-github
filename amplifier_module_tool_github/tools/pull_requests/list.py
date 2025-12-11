"""List pull requests in a repository."""

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


class ListPullRequestsTool(GitHubBaseTool):
    """Tool to list pull requests in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_pull_requests"

    @property
    def description(self) -> str:
        return (
            "List pull requests in a GitHub repository. Returns a list of PRs with their "
            "basic information including number, title, state, author, labels, and dates. "
            "Supports filtering by state (open/closed/all), labels, and sorting options. "
            "Includes draft PRs in results."
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
                    "description": "Filter by PR state (default: open)",
                    "default": "open"
                },
                "head": {
                    "type": "string",
                    "description": "Filter by head branch (format: 'user:branch')"
                },
                "base": {
                    "type": "string",
                    "description": "Filter by base branch"
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "popularity", "long-running"],
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
                    "description": "Maximum number of PRs to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List pull requests in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        state = input_data.get("state", "open")
        head = input_data.get("head")
        base = input_data.get("base")
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

            # Get pull requests with filters
            pulls = repo.get_pulls(
                state=state,
                sort=sort,
                direction=direction,
                base=base if base else None,
                head=head if head else None,
            )

            # Collect PR data
            pr_list = []
            count = 0
            for pr in pulls:
                if count >= limit:
                    break

                pr_data = {
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "draft": pr.draft,
                    "author": pr.user.login if pr.user else None,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "merged": pr.merged,
                    "mergeable": pr.mergeable,
                    "labels": [label.name for label in pr.labels],
                    "assignees": [assignee.login for assignee in pr.assignees],
                    "reviewers": [reviewer.login for reviewer in pr.requested_reviewers],
                    "head": {
                        "ref": pr.head.ref,
                        "sha": pr.head.sha,
                    },
                    "base": {
                        "ref": pr.base.ref,
                        "sha": pr.base.sha,
                    },
                    "comments": pr.comments,
                    "review_comments": pr.review_comments,
                    "commits": pr.commits,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files,
                    "url": pr.html_url,
                }
                pr_list.append(pr_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "state": state,
                    "count": len(pr_list),
                    "pull_requests": pr_list,
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
