"""Create a new pull request."""

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


class CreatePullRequestTool(GitHubBaseTool):
    """Tool to create a new pull request in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_pull_request"

    @property
    def description(self) -> str:
        return (
            "Create a new pull request in a GitHub repository. Requires write access. "
            "Can set title, body, base branch, head branch, reviewers, labels, and draft status."
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
                    "description": "Pull request title (required)"
                },
                "head": {
                    "type": "string",
                    "description": "The name of the branch where changes are (required)"
                },
                "base": {
                    "type": "string",
                    "description": "The name of the branch to merge into (required)"
                },
                "body": {
                    "type": "string",
                    "description": "Pull request body/description (supports Markdown)"
                },
                "draft": {
                    "type": "boolean",
                    "description": "Create as draft PR (default: false)",
                    "default": False
                },
                "maintainer_can_modify": {
                    "type": "boolean",
                    "description": "Allow maintainers to modify the PR (default: true)",
                    "default": True
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to add to the PR"
                },
                "assignees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Usernames to assign to the PR"
                },
                "reviewers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Usernames to request reviews from"
                },
                "team_reviewers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Team slugs to request reviews from"
                }
            },
            "required": ["repository", "title", "head", "base"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new pull request."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        title = input_data.get("title")
        head = input_data.get("head")
        base = input_data.get("base")
        body = input_data.get("body")
        draft = input_data.get("draft", False)
        maintainer_can_modify = input_data.get("maintainer_can_modify", True)
        labels = input_data.get("labels", [])
        assignees = input_data.get("assignees", [])
        reviewers = input_data.get("reviewers", [])
        team_reviewers = input_data.get("team_reviewers", [])

        if not repository or not title or not head or not base:
            return ToolResult(
                success=False,
                error={
                    "message": "repository, title, head, and base parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not title.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Pull request title cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)

            # Create the pull request
            pr = repo.create_pull(
                title=title,
                body=body or "",
                head=head,
                base=base,
                draft=draft,
                maintainer_can_modify=maintainer_can_modify,
            )

            # Add labels if specified
            if labels:
                try:
                    pr.add_to_labels(*labels)
                except Exception as e:
                    # Continue even if labels fail
                    pass

            # Add assignees if specified
            if assignees:
                try:
                    pr.add_to_assignees(*assignees)
                except Exception as e:
                    # Continue even if assignees fail
                    pass

            # Request reviewers if specified
            if reviewers or team_reviewers:
                try:
                    pr.create_review_request(
                        reviewers=reviewers if reviewers else [],
                        team_reviewers=team_reviewers if team_reviewers else []
                    )
                except Exception as e:
                    # Continue even if review requests fail
                    pass

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "pull_request": {
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "draft": pr.draft,
                        "head": pr.head.ref,
                        "base": pr.base.ref,
                        "url": pr.html_url,
                        "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    },
                    "message": f"Pull request #{pr.number} created successfully"
                }
            )

        except RepositoryNotFoundError as e:
            return ToolResult(success=False, error=e.to_dict())

        except RateLimitError as e:
            return ToolResult(success=False, error=e.to_dict())

        except GithubException as e:
            # Check for specific errors
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create pull request").to_dict()
                )
            elif e.status == 422:
                # Validation error (e.g., no commits between branches)
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Validation error: {str(e)}",
                        "code": "VALIDATION_ERROR"
                    }
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
