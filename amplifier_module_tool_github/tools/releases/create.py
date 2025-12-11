"""Create a new release."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    RateLimitError,
    PermissionError,
    ValidationError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class CreateReleaseTool(GitHubBaseTool):
    """Tool to create a new release in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_release"

    @property
    def description(self) -> str:
        return (
            "Create a new release in a GitHub repository. Can set as draft or pre-release. "
            "Requires write access. Note: Asset uploads are not supported through this tool; "
            "use the GitHub API directly for uploading release assets."
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
                "tag_name": {
                    "type": "string",
                    "description": "Git tag for the release (required, will be created if doesn't exist)"
                },
                "name": {
                    "type": "string",
                    "description": "Release title/name"
                },
                "body": {
                    "type": "string",
                    "description": "Release description/notes (supports Markdown)"
                },
                "draft": {
                    "type": "boolean",
                    "description": "Create as draft release (default: false)",
                    "default": False
                },
                "prerelease": {
                    "type": "boolean",
                    "description": "Mark as pre-release (default: false)",
                    "default": False
                },
                "target_commitish": {
                    "type": "string",
                    "description": "Branch or commit SHA to create tag from (default: repository's default branch)"
                },
                "generate_release_notes": {
                    "type": "boolean",
                    "description": "Automatically generate release notes (default: false)",
                    "default": False
                }
            },
            "required": ["repository", "tag_name"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new release."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        tag_name = input_data.get("tag_name")
        name = input_data.get("name")
        body = input_data.get("body")
        draft = input_data.get("draft", False)
        prerelease = input_data.get("prerelease", False)
        target_commitish = input_data.get("target_commitish")
        generate_release_notes = input_data.get("generate_release_notes", False)

        if not repository or not tag_name:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and tag_name parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not tag_name.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Tag name cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)

            # Prepare release parameters
            release_kwargs = {
                "tag": tag_name,
                "name": name or tag_name,
                "message": body or "",
                "draft": draft,
                "prerelease": prerelease,
            }

            if target_commitish:
                release_kwargs["target_commitish"] = target_commitish

            # Note: generate_release_notes is a newer GitHub API feature
            # It may not be supported in older PyGithub versions
            if generate_release_notes:
                try:
                    release_kwargs["generate_release_notes"] = generate_release_notes
                except Exception:
                    pass

            # Create the release
            release = repo.create_git_release(**release_kwargs)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "release": {
                        "id": release.id,
                        "tag_name": release.tag_name,
                        "name": release.title,
                        "draft": release.draft,
                        "prerelease": release.prerelease,
                        "url": release.html_url,
                        "created_at": release.created_at.isoformat() if release.created_at else None,
                    },
                    "message": f"Release '{release.tag_name}' created successfully"
                }
            )

        except RepositoryNotFoundError as e:
            return ToolResult(success=False, error=e.to_dict())

        except RateLimitError as e:
            return ToolResult(success=False, error=e.to_dict())

        except GithubException as e:
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create release").to_dict()
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

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Unexpected error: {str(e)}",
                    "code": "UNEXPECTED_ERROR"
                }
            )
