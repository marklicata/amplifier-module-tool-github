"""List workflows in a repository."""

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


class ListWorkflowsTool(GitHubBaseTool):
    """Tool to list GitHub Actions workflows in a repository."""

    @property
    def name(self) -> str:
        return "github_list_workflows"

    @property
    def description(self) -> str:
        return (
            "List all GitHub Actions workflows in a repository. Returns workflow names, "
            "IDs, paths, and states."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "Full repository name in format 'owner/repo' (e.g., 'microsoft/vscode')"
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List workflows in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)
            workflows = repo.get_workflows()

            # Collect workflow data
            workflow_list = []
            for workflow in workflows:
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
                workflow_list.append(workflow_data)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "count": len(workflow_list),
                    "workflows": workflow_list,
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
