"""List branches in a repository."""

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


class ListBranchesTool(GitHubBaseTool):
    """Tool to list branches in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_branches"

    @property
    def description(self) -> str:
        return (
            "List all branches in a GitHub repository. Returns branch names, SHAs, "
            "and protection status for each branch."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "[Required] Full repository name in format 'owner/repo' (e.g., 'microsoft/vscode'). This is a repository-specific operation."
                },
                "protected": {
                    "type": "boolean",
                    "description": "Filter by protection status (true=protected only, false=unprotected only, null=all)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of branches to return (default: 100, max: 100)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List branches in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        protected = input_data.get("protected")
        limit = input_data.get("limit", 100)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)
            branches = repo.get_branches()

            # Collect branch data
            branch_list = []
            count = 0
            for branch in branches:
                if count >= limit:
                    break

                # Check protection status
                is_protected = branch.protected

                # Filter by protection status if specified
                if protected is not None:
                    if protected and not is_protected:
                        continue
                    if not protected and is_protected:
                        continue

                branch_data = {
                    "name": branch.name,
                    "sha": branch.commit.sha,
                    "protected": is_protected,
                }

                # Get commit info
                try:
                    commit = branch.commit
                    branch_data["commit"] = {
                        "sha": commit.sha,
                        "url": commit.html_url if hasattr(commit, 'html_url') else None,
                    }
                except Exception:
                    pass

                branch_list.append(branch_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "count": len(branch_list),
                    "branches": branch_list,
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
