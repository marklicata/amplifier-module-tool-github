"""List workflow runs."""

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


class ListWorkflowRunsTool(GitHubBaseTool):
    """Tool to list GitHub Actions workflow runs."""

    @property
    def name(self) -> str:
        return "github_list_workflow_runs"

    @property
    def description(self) -> str:
        return (
            "List workflow runs for a repository or specific workflow. Returns run information "
            "including status, conclusion, timestamps, and triggering details. "
            "Can filter by status, conclusion, branch, and actor."
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
                "workflow_id": {
                    "type": ["integer", "string"],
                    "description": "Filter by workflow ID or filename (optional, if omitted returns all workflows)"
                },
                "status": {
                    "type": "string",
                    "enum": ["queued", "in_progress", "completed"],
                    "description": "Filter by status"
                },
                "conclusion": {
                    "type": "string",
                    "enum": ["success", "failure", "cancelled", "skipped", "timed_out", "action_required"],
                    "description": "Filter by conclusion (only for completed runs)"
                },
                "branch": {
                    "type": "string",
                    "description": "Filter by branch name"
                },
                "actor": {
                    "type": "string",
                    "description": "Filter by the user who triggered the run"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of runs to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List workflow runs."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        workflow_id = input_data.get("workflow_id")
        status = input_data.get("status")
        conclusion = input_data.get("conclusion")
        branch = input_data.get("branch")
        actor = input_data.get("actor")
        limit = input_data.get("limit", 30)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get workflow runs
            if workflow_id:
                workflow = repo.get_workflow(workflow_id)
                runs = workflow.get_runs(
                    status=status,
                    branch=branch,
                    actor=actor,
                )
            else:
                runs = repo.get_workflow_runs(
                    status=status,
                    branch=branch,
                    actor=actor,
                )

            # Collect run data
            run_list = []
            count = 0
            for run in runs:
                if count >= limit:
                    break

                # Filter by conclusion if specified (only for completed runs)
                if conclusion and run.conclusion != conclusion:
                    continue

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
                }

                run_list.append(run_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "workflow_id": workflow_id,
                    "count": len(run_list),
                    "runs": run_list,
                }
            )

        except GithubException as e:
            if e.status == 404:
                if workflow_id:
                    return ToolResult(
                        success=False,
                        error={
                            "message": f"Workflow '{workflow_id}' not found in repository '{repository}'",
                            "code": "WORKFLOW_NOT_FOUND"
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
