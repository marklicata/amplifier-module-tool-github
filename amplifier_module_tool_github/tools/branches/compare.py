"""Compare two branches."""

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


class CompareBranchesTool(GitHubBaseTool):
    """Tool to compare two branches in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_compare_branches"

    @property
    def description(self) -> str:
        return (
            "Compare two branches (or commits/tags) in a GitHub repository. Returns the diff "
            "between them including files changed, commit history, and statistics. "
            "Shows what changes exist in the head ref that don't exist in the base ref."
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
                "base": {
                    "type": "string",
                    "description": "Base branch/commit/tag to compare from (required)"
                },
                "head": {
                    "type": "string",
                    "description": "Head branch/commit/tag to compare to (required)"
                },
                "include_files": {
                    "type": "boolean",
                    "description": "Include list of files changed (default: true)",
                    "default": True
                },
                "include_commits": {
                    "type": "boolean",
                    "description": "Include list of commits (default: true)",
                    "default": True
                }
            },
            "required": ["repository", "base", "head"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Compare two branches."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        base = input_data.get("base")
        head = input_data.get("head")
        include_files = input_data.get("include_files", True)
        include_commits = input_data.get("include_commits", True)

        if not repository or not base or not head:
            return ToolResult(
                success=False,
                error={
                    "message": "repository, base, and head parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)

            # Compare the refs
            comparison = repo.compare(base, head)

            comparison_data = {
                "base": {
                    "ref": base,
                    "sha": comparison.base_commit.sha,
                },
                "head": {
                    "ref": head,
                    "sha": comparison.head_commit.sha,
                },
                "status": comparison.status,
                "ahead_by": comparison.ahead_by,
                "behind_by": comparison.behind_by,
                "total_commits": comparison.total_commits,
                "stats": {
                    "additions": comparison.additions if hasattr(comparison, 'additions') else 0,
                    "deletions": comparison.deletions if hasattr(comparison, 'deletions') else 0,
                    "total": comparison.total_commits,
                },
                "url": comparison.html_url,
            }

            # Include files changed if requested
            if include_files:
                files = []
                for file in comparison.files:
                    file_data = {
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                    }
                    # Include patch if available
                    if hasattr(file, 'patch') and file.patch:
                        file_data["patch"] = file.patch
                    files.append(file_data)
                comparison_data["files"] = files
                comparison_data["files_changed"] = len(files)

            # Include commits if requested
            if include_commits:
                commits = []
                for commit in comparison.commits:
                    commits.append({
                        "sha": commit.sha,
                        "message": commit.commit.message if commit.commit else None,
                        "author": {
                            "name": commit.commit.author.name if commit.commit and commit.commit.author else None,
                            "email": commit.commit.author.email if commit.commit and commit.commit.author else None,
                            "date": commit.commit.author.date.isoformat() if commit.commit and commit.commit.author and commit.commit.author.date else None,
                            "username": commit.author.login if commit.author else None,
                        },
                        "url": commit.html_url,
                    })
                comparison_data["commits"] = commits

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "comparison": comparison_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"One or both references not found: base='{base}', head='{head}'",
                        "code": "REF_NOT_FOUND"
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
