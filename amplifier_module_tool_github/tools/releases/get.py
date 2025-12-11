"""Get release details."""

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


class GetReleaseTool(GitHubBaseTool):
    """Tool to get detailed information about a specific release."""

    @property
    def name(self) -> str:
        return "github_get_release"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific release in a GitHub repository. "
            "Can retrieve by release ID or tag name. Returns release metadata, "
            "description, assets, and download statistics."
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
                "release_id": {
                    "type": "integer",
                    "description": "Release ID (use either release_id or tag_name)"
                },
                "tag_name": {
                    "type": "string",
                    "description": "Tag name (use either release_id or tag_name, or 'latest' for latest release)"
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get release details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        release_id = input_data.get("release_id")
        tag_name = input_data.get("tag_name")

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        if not release_id and not tag_name:
            return ToolResult(
                success=False,
                error={
                    "message": "Either release_id or tag_name parameter is required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get release by ID or tag
            if release_id:
                release = repo.get_release(release_id)
            elif tag_name == "latest":
                release = repo.get_latest_release()
            else:
                release = repo.get_release(tag_name)

            release_data = {
                "id": release.id,
                "tag_name": release.tag_name,
                "name": release.title,
                "body": release.body,
                "draft": release.draft,
                "prerelease": release.prerelease,
                "created_at": release.created_at.isoformat() if release.created_at else None,
                "published_at": release.published_at.isoformat() if release.published_at else None,
                "author": {
                    "login": release.author.login if release.author else None,
                    "url": release.author.html_url if release.author else None,
                },
                "url": release.html_url,
                "target_commitish": release.target_commitish,
                "tarball_url": release.tarball_url,
                "zipball_url": release.zipball_url,
            }

            # Get assets with full details
            assets = []
            total_downloads = 0
            for asset in release.get_assets():
                asset_data = {
                    "id": asset.id,
                    "name": asset.name,
                    "label": asset.label,
                    "size": asset.size,
                    "download_count": asset.download_count,
                    "content_type": asset.content_type,
                    "state": asset.state,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None,
                    "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
                    "url": asset.browser_download_url,
                }
                assets.append(asset_data)
                total_downloads += asset.download_count

            release_data["assets"] = assets
            release_data["assets_count"] = len(assets)
            release_data["total_downloads"] = total_downloads

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "release": release_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                identifier = f"ID {release_id}" if release_id else f"tag '{tag_name}'"
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Release {identifier} not found in repository '{repository}'",
                        "code": "RELEASE_NOT_FOUND"
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
