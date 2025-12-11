"""Get repository details."""

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


class GetRepositoryTool(GitHubBaseTool):
    """Tool to get detailed information about a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_get_repository"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a GitHub repository. Returns repository metadata "
            "including description, statistics, settings, and more."
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
        """Get repository details."""
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

            repo_data = {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "fork": repo.fork,
                "archived": repo.archived,
                "disabled": repo.disabled,
                "owner": {
                    "login": repo.owner.login,
                    "type": repo.owner.type,
                    "url": repo.owner.html_url,
                },
                "html_url": repo.html_url,
                "homepage": repo.homepage,
                "language": repo.language,
                "default_branch": repo.default_branch,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                "size": repo.size,
                "stargazers_count": repo.stargazers_count,
                "watchers_count": repo.watchers_count,
                "forks_count": repo.forks_count,
                "open_issues_count": repo.open_issues_count,
                "has_issues": repo.has_issues,
                "has_projects": repo.has_projects,
                "has_downloads": repo.has_downloads,
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "has_discussions": repo.has_discussions if hasattr(repo, 'has_discussions') else None,
                "license": repo.license.name if repo.license else None,
                "topics": repo.get_topics() if hasattr(repo, 'get_topics') else [],
                "visibility": repo.visibility if hasattr(repo, 'visibility') else None,
                "allow_forking": repo.allow_forking if hasattr(repo, 'allow_forking') else None,
                "is_template": repo.is_template if hasattr(repo, 'is_template') else None,
            }

            # Get permissions if available
            try:
                permissions = repo.permissions
                if permissions:
                    repo_data["permissions"] = {
                        "admin": permissions.admin,
                        "push": permissions.push,
                        "pull": permissions.pull,
                    }
            except Exception:
                pass

            return ToolResult(
                success=True,
                output={
                    "repository": repo_data,
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
