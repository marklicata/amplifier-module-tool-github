"""Rerun a workflow."""

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


class RerunWorkflowTool(GitHubBaseTool):
    """Tool to rerun a GitHub Actions workflow."""

    @property
    def name(self) -> str:
        return "github_rerun_workflow"

    @property
    def description(self) -> str:
        return (
            "Rerun a GitHub Actions workflow run. Can rerun all jobs or only failed jobs. "
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
                "run_id": {
                    "type": "integer",
                    "description": "Workflow run ID to rerun (required)"
                },
                "failed_jobs_only": {
                    "type": "boolean",
                    "description": "Rerun only failed jobs (default: false, rerun all jobs)",
                    "default": False
                }
            },
            "required": ["repository", "run_id"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Rerun a workflow."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        run_id = input_data.get("run_id")
        failed_jobs_only = input_data.get("failed_jobs_only", False)

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

            # Check if run is in a state that can be rerun
            if run.status != "completed":
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Workflow run #{run_id} is not completed and cannot be rerun",
                        "code": "RUN_NOT_COMPLETED"
                    }
                )

            # Rerun the workflow
            if failed_jobs_only:
                result = run.rerun_failed_jobs()
                message = f"Workflow run #{run_id} rerun requested for failed jobs"
            else:
                result = run.rerun()
                message = f"Workflow run #{run_id} rerun requested for all jobs"

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "run": {
                        "id": run.id,
                        "name": run.name,
                        "failed_jobs_only": failed_jobs_only,
                    },
                    "message": message
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
                    error=PermissionError("rerun workflow").to_dict()
                )
            elif e.status == 409:
                return ToolResult(
                    success=False,
                    error={
                        "message": "Workflow run cannot be rerun (may already be running)",
                        "code": "CANNOT_RERUN"
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
