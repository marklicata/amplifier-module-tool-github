"""List tags in a repository."""

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


class ListTagsTool(GitHubBaseTool):
    """Tool to list tags in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_tags"

    @property
    def description(self) -> str:
        return (
            "List all tags in a GitHub repository. Returns tag names, commit SHAs, "
            "and commit information for each tag."
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
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tags to return (default: 100, max: 100)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List tags in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        limit = input_data.get("limit", 100)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)
            tags = repo.get_tags()

            # Collect tag data
            tag_list = []
            count = 0
            for tag in tags:
                if count >= limit:
                    break

                tag_data = {
                    "name": tag.name,
                    "commit": {
                        "sha": tag.commit.sha,
                        "url": tag.commit.html_url if hasattr(tag.commit, 'html_url') else None,
                    },
                    "zipball_url": tag.zipball_url,
                    "tarball_url": tag.tarball_url,
                }

                tag_list.append(tag_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "count": len(tag_list),
                    "tags": tag_list,
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
