"""Merge a pull request."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    RateLimitError,
    PermissionError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class MergePullRequestTool(GitHubBaseTool):
    """Tool to merge a pull request."""

    @property
    def name(self) -> str:
        return "github_merge_pull_request"

    @property
    def description(self) -> str:
        return (
            "Merge a pull request in a GitHub repository. Supports different merge strategies: "
            "merge (standard merge commit), squash (squash and merge), or rebase (rebase and merge). "
            "Can optionally delete the branch after merging. Requires write access."
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
                "merge_method": {
                    "type": "string",
                    "enum": ["merge", "squash", "rebase"],
                    "description": "Merge method to use (default: merge)",
                    "default": "merge"
                },
                "commit_title": {
                    "type": "string",
                    "description": "Custom commit title for the merge"
                },
                "commit_message": {
                    "type": "string",
                    "description": "Custom commit message for the merge"
                },
                "sha": {
                    "type": "string",
                    "description": "SHA that pull request head must match to allow merge"
                },
                "delete_branch": {
                    "type": "boolean",
                    "description": "Delete the branch after merging (default: false)",
                    "default": False
                }
            },
            "required": ["repository", "pull_number"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Merge a pull request."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        pull_number = input_data.get("pull_number")
        merge_method = input_data.get("merge_method", "merge")
        commit_title = input_data.get("commit_title")
        commit_message = input_data.get("commit_message")
        sha = input_data.get("sha")
        delete_branch = input_data.get("delete_branch", False)

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

            # Check if PR is already merged
            if pr.merged:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Pull request #{pull_number} is already merged",
                        "code": "ALREADY_MERGED"
                    }
                )

            # Check if PR is closed without merging
            if pr.state == "closed":
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Pull request #{pull_number} is closed and cannot be merged",
                        "code": "PR_CLOSED"
                    }
                )

            # Merge the pull request
            merge_kwargs = {
                "merge_method": merge_method,
            }
            if commit_title:
                merge_kwargs["commit_title"] = commit_title
            if commit_message:
                merge_kwargs["commit_message"] = commit_message
            if sha:
                merge_kwargs["sha"] = sha

            merge_result = pr.merge(**merge_kwargs)

            # Delete branch if requested
            branch_deleted = False
            if delete_branch and merge_result.merged:
                try:
                    # Get the head ref
                    ref = repo.get_git_ref(f"heads/{pr.head.ref}")
                    ref.delete()
                    branch_deleted = True
                except Exception:
                    # Branch deletion failed, but merge succeeded
                    pass

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "pull_request": {
                        "number": pr.number,
                        "title": pr.title,
                        "merged": merge_result.merged,
                        "sha": merge_result.sha,
                        "message": merge_result.message,
                        "branch_deleted": branch_deleted,
                    },
                    "message": f"Pull request #{pr.number} merged successfully"
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
                    error=PermissionError("merge pull request").to_dict()
                )
            elif e.status == 405:
                return ToolResult(
                    success=False,
                    error={
                        "message": "Pull request is not mergeable",
                        "code": "NOT_MERGEABLE"
                    }
                )
            elif e.status == 409:
                return ToolResult(
                    success=False,
                    error={
                        "message": "SHA mismatch or merge conflict",
                        "code": "MERGE_CONFLICT"
                    }
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
