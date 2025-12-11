"""Cancel a workflow run."""

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


class CancelWorkflowRunTool(GitHubBaseTool):
    """Tool to cancel a running GitHub Actions workflow."""

    @property
    def name(self) -> str:
        return "github_cancel_workflow_run"

    @property
    def description(self) -> str:
        return (
            "Cancel a running GitHub Actions workflow run. Only works for runs that are "
            "in 'queued' or 'in_progress' status. Requires write access to the repository."
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
                "run_id": {
                    "type": "integer",
                    "description": "Workflow run ID to cancel (required)"
                }
            },
            "required": ["repository", "run_id"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Cancel a workflow run."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        run_id = input_data.get("run_id")

        if not repository or run_id is None:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and run_id parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            run = repo.get_workflow_run(run_id)

            # Check if run can be cancelled
            if run.status == "completed":
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Workflow run #{run_id} is already completed and cannot be cancelled",
                        "code": "RUN_ALREADY_COMPLETED"
                    }
                )

            # Cancel the run
            result = run.cancel()

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "run": {
                        "id": run.id,
                        "name": run.name,
                        "status": "cancelling",
                    },
                    "message": f"Workflow run #{run_id} cancellation requested"
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Workflow run #{run_id} not found in repository '{repository}'",
                        "code": "RUN_NOT_FOUND"
                    }
                )
            elif e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("cancel workflow run").to_dict()
                )
            elif e.status == 409:
                return ToolResult(
                    success=False,
                    error={
                        "message": "Workflow run cannot be cancelled (may already be cancelled or completed)",
                        "code": "CANNOT_CANCEL"
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
