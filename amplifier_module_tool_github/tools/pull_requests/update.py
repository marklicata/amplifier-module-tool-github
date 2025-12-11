"""Update an existing pull request."""

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


class UpdatePullRequestTool(GitHubBaseTool):
    """Tool to update an existing pull request."""

    @property
    def name(self) -> str:
        return "github_update_pull_request"

    @property
    def description(self) -> str:
        return (
            "Update an existing pull request in a GitHub repository. Can update title, body, "
            "state (open/closed), base branch, labels, assignees, and reviewers. "
            "Requires write access to the repository."
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
                "pull_number": {
                    "type": "integer",
                    "description": "Pull request number"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the PR"
                },
                "body": {
                    "type": "string",
                    "description": "New body/description for the PR"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed"],
                    "description": "Change PR state to open or closed"
                },
                "base": {
                    "type": "string",
                    "description": "Change the base branch"
                },
                "maintainer_can_modify": {
                    "type": "boolean",
                    "description": "Allow maintainers to modify the PR"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Replace all labels with these (empty array to remove all)"
                },
                "assignees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Replace all assignees with these (empty array to remove all)"
                },
                "add_reviewers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Add reviewers to the PR"
                },
                "remove_reviewers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Remove reviewers from the PR"
                }
            },
            "required": ["repository", "pull_number"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Update a pull request."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        pull_number = input_data.get("pull_number")
        title = input_data.get("title")
        body = input_data.get("body")
        state = input_data.get("state")
        base = input_data.get("base")
        maintainer_can_modify = input_data.get("maintainer_can_modify")
        labels = input_data.get("labels")
        assignees = input_data.get("assignees")
        add_reviewers = input_data.get("add_reviewers", [])
        remove_reviewers = input_data.get("remove_reviewers", [])

        if not repository or pull_number is None:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and pull_number parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            pr = repo.get_pull(pull_number)

            # Update PR fields
            update_kwargs = {}
            if title is not None:
                if not title.strip():
                    return ToolResult(
                        success=False,
                        error=ValidationError("Pull request title cannot be empty").to_dict()
                    )
                update_kwargs["title"] = title
            if body is not None:
                update_kwargs["body"] = body
            if state is not None:
                update_kwargs["state"] = state
            if base is not None:
                update_kwargs["base"] = base
            if maintainer_can_modify is not None:
                update_kwargs["maintainer_can_modify"] = maintainer_can_modify

            if update_kwargs:
                pr.edit(**update_kwargs)

            # Update labels if specified
            if labels is not None:
                try:
                    pr.set_labels(*labels)
                except Exception as e:
                    # Continue even if labels fail
                    pass

            # Update assignees if specified
            if assignees is not None:
                try:
                    # Remove all current assignees
                    current_assignees = [a.login for a in pr.assignees]
                    if current_assignees:
                        pr.remove_from_assignees(*current_assignees)
                    # Add new assignees
                    if assignees:
                        pr.add_to_assignees(*assignees)
                except Exception as e:
                    # Continue even if assignees fail
                    pass

            # Add reviewers if specified
            if add_reviewers:
                try:
                    pr.create_review_request(reviewers=add_reviewers)
                except Exception as e:
                    # Continue even if review requests fail
                    pass

            # Remove reviewers if specified
            if remove_reviewers:
                try:
                    pr.delete_review_request(reviewers=remove_reviewers)
                except Exception as e:
                    # Continue even if removing reviewers fails
                    pass

            # Reload PR to get updated data
            pr = repo.get_pull(pull_number)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "pull_request": {
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "draft": pr.draft,
                        "url": pr.html_url,
                        "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    },
                    "message": f"Pull request #{pr.number} updated successfully"
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Pull request #{pull_number} not found in {repository}",
                        "code": "PR_NOT_FOUND"
                    }
                )
            elif e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("update pull request").to_dict()
                )
            return ToolResult(
                success=False,
                error={
                    "message": f"GitHub API error: {str(e)}",
                    "code": "GITHUB_API_ERROR"
                }
            )

        except RepositoryNotFoundError as e:
            return ToolResult(success=False, error=e.to_dict())

        except RateLimitError as e:
            return ToolResult(success=False, error=e.to_dict())

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Unexpected error: {str(e)}",
                    "code": "UNEXPECTED_ERROR"
                }
            )
