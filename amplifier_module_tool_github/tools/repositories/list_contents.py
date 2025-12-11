"""List repository contents."""

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


class ListRepositoryContentsTool(GitHubBaseTool):
    """Tool to list contents of a directory in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_repository_contents"

    @property
    def description(self) -> str:
        return (
            "List the contents of a directory in a GitHub repository. Returns files and "
            "subdirectories with their metadata. Can optionally list contents recursively."
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
                "path": {
                    "type": "string",
                    "description": "Path to directory in repository (empty string or '/' for root)",
                    "default": ""
                },
                "ref": {
                    "type": "string",
                    "description": "Git reference (branch, tag, or commit SHA). Defaults to repository's default branch"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "List contents recursively (default: false)",
                    "default": False
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List repository contents."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        path = input_data.get("path", "")
        ref = input_data.get("ref")
        recursive = input_data.get("recursive", False)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get contents
            kwargs = {"path": path or ""}
            if ref:
                kwargs["ref"] = ref

            contents = repo.get_contents(**kwargs)

            # Handle single file vs directory
            if not isinstance(contents, list):
                contents = [contents]

            def process_contents(items, current_path=""):
                """Process contents recursively if needed."""
                result = []
                for item in items:
                    item_data = {
                        "name": item.name,
                        "path": item.path,
                        "type": item.type,
                        "size": item.size,
                        "sha": item.sha,
                        "url": item.html_url,
                        "download_url": item.download_url,
                    }
                    result.append(item_data)

                    # If recursive and item is a directory, get its contents
                    if recursive and item.type == "dir":
                        try:
                            sub_kwargs = {"path": item.path}
                            if ref:
                                sub_kwargs["ref"] = ref
                            sub_contents = repo.get_contents(**sub_kwargs)
                            if isinstance(sub_contents, list):
                                sub_items = process_contents(sub_contents, item.path)
                                result.extend(sub_items)
                        except Exception:
                            # Skip directories that can't be read
                            pass

                return result

            contents_list = process_contents(contents)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "path": path or "/",
                    "ref": ref or repo.default_branch,
                    "recursive": recursive,
                    "count": len(contents_list),
                    "contents": contents_list,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Path '{path}' not found in repository '{repository}'",
                        "code": "PATH_NOT_FOUND"
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
