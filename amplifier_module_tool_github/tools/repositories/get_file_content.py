"""Get file content from a repository."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RepositoryNotFoundError,
    RateLimitError,
    GitHubError,
)
import base64

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class GetFileContentTool(GitHubBaseTool):
    """Tool to get file content from a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_get_file_content"

    @property
    def description(self) -> str:
        return (
            "Get the content of a file from a GitHub repository. Supports different refs "
            "(branches, tags, commit SHAs). Returns file content, encoding, size, and metadata."
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
                    "description": "Path to the file in the repository (e.g., 'src/main.py')"
                },
                "ref": {
                    "type": "string",
                    "description": "Git reference (branch, tag, or commit SHA). Defaults to repository's default branch"
                },
                "decode": {
                    "type": "boolean",
                    "description": "Decode the content from base64 to string (default: true)",
                    "default": True
                }
            },
            "required": ["repository", "path"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get file content from a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        path = input_data.get("path")
        ref = input_data.get("ref")
        decode = input_data.get("decode", True)

        if not repository or not path:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and path parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get file content
            kwargs = {"path": path}
            if ref:
                kwargs["ref"] = ref

            content_file = repo.get_contents(**kwargs)

            # Handle if it's a directory
            if isinstance(content_file, list):
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Path '{path}' is a directory, not a file",
                        "code": "PATH_IS_DIRECTORY"
                    }
                )

            # Get file content
            file_content = content_file.content
            if decode and file_content:
                try:
                    # Content is base64 encoded
                    decoded_content = base64.b64decode(file_content).decode('utf-8')
                    content = decoded_content
                    encoding = "utf-8"
                except Exception:
                    # If decode fails, return base64
                    content = file_content
                    encoding = "base64"
            else:
                content = file_content
                encoding = content_file.encoding

            file_data = {
                "name": content_file.name,
                "path": content_file.path,
                "sha": content_file.sha,
                "size": content_file.size,
                "content": content,
                "encoding": encoding,
                "type": content_file.type,
                "url": content_file.html_url,
                "download_url": content_file.download_url,
            }

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "ref": ref or repo.default_branch,
                    "file": file_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"File '{path}' not found in repository '{repository}'",
                        "code": "FILE_NOT_FOUND"
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
