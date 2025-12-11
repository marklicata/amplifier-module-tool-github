"""Trigger a workflow run."""

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


class TriggerWorkflowTool(GitHubBaseTool):
    """Tool to manually trigger a GitHub Actions workflow."""

    @property
    def name(self) -> str:
        return "github_trigger_workflow"

    @property
    def description(self) -> str:
        return (
            "Manually trigger a GitHub Actions workflow run using workflow_dispatch event. "
            "Can pass inputs to the workflow. Requires write access to the repository."
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
                },
                "ref": {
                    "type": "string",
                    "description": "Git reference (branch or tag) to run workflow on (default: repository's default branch)"
                },
                "inputs": {
                    "type": "object",
                    "description": "Input parameters for the workflow (key-value pairs)",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["repository", "workflow_id"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Trigger a workflow run."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        workflow_id = input_data.get("workflow_id")
        ref = input_data.get("ref")
        inputs = input_data.get("inputs", {})

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

            # Use default branch if ref not specified
            if not ref:
                ref = repo.default_branch

            # Trigger the workflow
            result = workflow.create_dispatch(ref=ref, inputs=inputs)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "workflow": {
                        "id": workflow.id,
                        "name": workflow.name,
                    },
                    "ref": ref,
                    "inputs": inputs,
                    "message": f"Workflow '{workflow.name}' triggered successfully on '{ref}'"
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
            elif e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("trigger workflow").to_dict()
                )
            elif e.status == 422:
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
