"""Get workflow run details."""

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


class GetWorkflowRunTool(GitHubBaseTool):
    """Tool to get detailed information about a specific workflow run."""

    @property
    def name(self) -> str:
        return "github_get_workflow_run"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific GitHub Actions workflow run. "
            "Returns run metadata, jobs, steps, and logs information."
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
                    "description": "Workflow run ID (required)"
                },
                "include_jobs": {
                    "type": "boolean",
                    "description": "Include job details (default: true)",
                    "default": True
                }
            },
            "required": ["repository", "run_id"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get workflow run details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        run_id = input_data.get("run_id")
        include_jobs = input_data.get("include_jobs", True)

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

            run_data = {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "workflow_id": run.workflow_id,
                "run_number": run.run_number,
                "event": run.event,
                "head_branch": run.head_branch,
                "head_sha": run.head_sha,
                "created_at": run.created_at.isoformat() if run.created_at else None,
                "updated_at": run.updated_at.isoformat() if run.updated_at else None,
                "run_started_at": run.run_started_at.isoformat() if hasattr(run, 'run_started_at') and run.run_started_at else None,
                "actor": run.actor.login if run.actor else None,
                "url": run.html_url,
                "logs_url": run.logs_url,
                "cancel_url": run.cancel_url,
                "rerun_url": run.rerun_url,
            }

            # Include jobs if requested
            if include_jobs:
                jobs = []
                for job in run.jobs():
                    job_data = {
                        "id": job.id,
                        "name": job.name,
                        "status": job.status,
                        "conclusion": job.conclusion,
                        "started_at": job.started_at.isoformat() if job.started_at else None,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                        "url": job.html_url,
                    }

                    # Include steps
                    steps = []
                    for step in job.steps:
                        steps.append({
                            "name": step.name,
                            "status": step.status,
                            "conclusion": step.conclusion,
                            "number": step.number,
                            "started_at": step.started_at.isoformat() if step.started_at else None,
                            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                        })
                    job_data["steps"] = steps

                    jobs.append(job_data)

                run_data["jobs"] = jobs
                run_data["jobs_count"] = len(jobs)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "run": run_data,
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
