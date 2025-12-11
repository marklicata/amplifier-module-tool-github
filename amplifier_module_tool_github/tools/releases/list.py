"""List releases in a repository."""

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


class ListReleasesTool(GitHubBaseTool):
    """Tool to list releases in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_releases"

    @property
    def description(self) -> str:
        return (
            "List releases in a GitHub repository. Returns release information including "
            "version tags, titles, descriptions, assets, and download counts. "
            "Can include draft and pre-releases."
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
                "include_drafts": {
                    "type": "boolean",
                    "description": "Include draft releases (default: false)",
                    "default": False
                },
                "include_prereleases": {
                    "type": "boolean",
                    "description": "Include pre-releases (default: true)",
                    "default": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of releases to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List releases in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        include_drafts = input_data.get("include_drafts", False)
        include_prereleases = input_data.get("include_prereleases", True)
        limit = input_data.get("limit", 30)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)
            releases = repo.get_releases()

            # Collect release data
            release_list = []
            count = 0
            for release in releases:
                if count >= limit:
                    break

                # Filter drafts and pre-releases
                if release.draft and not include_drafts:
                    continue
                if release.prerelease and not include_prereleases:
                    continue

                release_data = {
                    "id": release.id,
                    "tag_name": release.tag_name,
                    "name": release.title,
                    "body": release.body,
                    "draft": release.draft,
                    "prerelease": release.prerelease,
                    "created_at": release.created_at.isoformat() if release.created_at else None,
                    "published_at": release.published_at.isoformat() if release.published_at else None,
                    "author": release.author.login if release.author else None,
                    "url": release.html_url,
                    "target_commitish": release.target_commitish,
                }

                # Get assets
                assets = []
                for asset in release.get_assets():
                    assets.append({
                        "id": asset.id,
                        "name": asset.name,
                        "label": asset.label,
                        "size": asset.size,
                        "download_count": asset.download_count,
                        "content_type": asset.content_type,
                        "state": asset.state,
                        "url": asset.browser_download_url,
                    })
                release_data["assets"] = assets
                release_data["assets_count"] = len(assets)

                release_list.append(release_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "count": len(release_list),
                    "releases": release_list,
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
