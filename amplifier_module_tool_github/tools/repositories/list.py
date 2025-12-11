"""List repositories for a user or organization."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RateLimitError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class ListRepositoriesTool(GitHubBaseTool):
    """Tool to list repositories for a user or organization."""

    @property
    def name(self) -> str:
        return "github_list_repositories"

    @property
    def description(self) -> str:
        return (
            "List repositories for a specific user or organization. Returns basic information "
            "about each repository. Can filter by type (all, public, private, forks, sources, member) "
            "and sort by various criteria."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "GitHub username or organization name"
                },
                "type": {
                    "type": "string",
                    "enum": ["all", "public", "private", "forks", "sources", "member"],
                    "description": "Filter by repository type (default: all)",
                    "default": "all"
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "pushed", "full_name"],
                    "description": "Sort field (default: full_name)",
                    "default": "full_name"
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort direction (default: asc)",
                    "default": "asc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of repositories to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["owner"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List repositories for a user or organization."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        owner = input_data.get("owner")
        repo_type = input_data.get("type", "all")
        sort = input_data.get("sort", "full_name")
        direction = input_data.get("direction", "asc")
        limit = input_data.get("limit", 30)

        if not owner:
            return ToolResult(
                success=False,
                error={"message": "owner parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            # Try to get as organization first, then as user
            try:
                org = self.manager.github.get_organization(owner)
                repos = org.get_repos(type=repo_type, sort=sort, direction=direction)
                owner_type = "organization"
            except GithubException as e:
                if e.status == 404:
                    # Not an organization, try as user
                    user = self.manager.github.get_user(owner)
                    repos = user.get_repos(type=repo_type, sort=sort, direction=direction)
                    owner_type = "user"
                else:
                    raise

            # Collect repository data
            repo_list = []
            count = 0
            for repo in repos:
                if count >= limit:
                    break

                repo_data = {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "fork": repo.fork,
                    "archived": repo.archived,
                    "language": repo.language,
                    "default_branch": repo.default_branch,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                    "stargazers_count": repo.stargazers_count,
                    "watchers_count": repo.watchers_count,
                    "forks_count": repo.forks_count,
                    "open_issues_count": repo.open_issues_count,
                    "url": repo.html_url,
                }
                repo_list.append(repo_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "owner": owner,
                    "owner_type": owner_type,
                    "type": repo_type,
                    "count": len(repo_list),
                    "repositories": repo_list,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"User or organization '{owner}' not found",
                        "code": "OWNER_NOT_FOUND"
                    }
                )
            return ToolResult(
                success=False,
                error={
                    "message": f"GitHub API error: {str(e)}",
                    "code": "GITHUB_API_ERROR"
                }
            )

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
