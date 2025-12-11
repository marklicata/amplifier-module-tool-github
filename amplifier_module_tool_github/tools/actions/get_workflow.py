"""Get workflow details."""

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


class GetWorkflowTool(GitHubBaseTool):
    """Tool to get detailed information about a specific workflow."""

    @property
    def name(self) -> str:
        return "github_get_workflow"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific GitHub Actions workflow. "
            "Returns workflow metadata, configuration, and statistics."
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
                    "description": "Workflow ID or workflow file name (e.g., 'main.yml')"
                }
            },
            "required": ["repository", "workflow_id"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get workflow details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        workflow_id = input_data.get("workflow_id")

        if not repository or not workflow_id:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and workflow_id parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            workflow = repo.get_workflow(workflow_id)

            workflow_data = {
                "id": workflow.id,
                "name": workflow.name,
                "path": workflow.path,
                "state": workflow.state,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
                "url": workflow.html_url,
                "badge_url": workflow.badge_url,
            }

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "workflow": workflow_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
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
