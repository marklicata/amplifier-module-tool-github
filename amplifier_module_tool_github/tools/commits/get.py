"""Get commit details."""

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


class GetCommitTool(GitHubBaseTool):
    """Tool to get detailed information about a specific commit."""

    @property
    def name(self) -> str:
        return "github_get_commit"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific commit in a GitHub repository. "
            "Returns commit message, author, stats, and list of files changed with diffs."
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
                "sha": {
                    "type": "string",
                    "description": "Commit SHA (required)"
                },
                "include_files": {
                    "type": "boolean",
                    "description": "Include list of files changed (default: true)",
                    "default": True
                }
            },
            "required": ["repository", "sha"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get commit details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        sha = input_data.get("sha")
        include_files = input_data.get("include_files", True)

        if not repository or not sha:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and sha parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            commit = repo.get_commit(sha)

            commit_data = {
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": {
                    "name": commit.commit.author.name if commit.commit.author else None,
                    "email": commit.commit.author.email if commit.commit.author else None,
                    "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None,
                    "username": commit.author.login if commit.author else None,
                    "avatar_url": commit.author.avatar_url if commit.author else None,
                },
                "committer": {
                    "name": commit.commit.committer.name if commit.commit.committer else None,
                    "email": commit.commit.committer.email if commit.commit.committer else None,
                    "date": commit.commit.committer.date.isoformat() if commit.commit.committer and commit.commit.committer.date else None,
                    "username": commit.committer.login if commit.committer else None,
                    "avatar_url": commit.committer.avatar_url if commit.committer else None,
                },
                "url": commit.html_url,
                "comment_count": commit.commit.comment_count if hasattr(commit.commit, 'comment_count') else 0,
                "stats": {
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                    "total": commit.stats.total,
                },
                "parents": [{"sha": parent.sha, "url": parent.html_url} for parent in commit.parents],
            }

            # Include files changed if requested
            if include_files:
                files = []
                for file in commit.files:
                    file_data = {
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                    }
                    # Include patch if available and not too large
                    if hasattr(file, 'patch') and file.patch:
                        file_data["patch"] = file.patch
                    files.append(file_data)
                commit_data["files"] = files

            # Get commit comments if any
            try:
                comments = []
                for comment in commit.get_comments():
                    comments.append({
                        "id": comment.id,
                        "user": comment.user.login if comment.user else None,
                        "body": comment.body,
                        "path": comment.path if hasattr(comment, 'path') else None,
                        "position": comment.position if hasattr(comment, 'position') else None,
                        "line": comment.line if hasattr(comment, 'line') else None,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                    })
                commit_data["comments"] = comments
            except Exception:
                commit_data["comments"] = []

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "commit": commit_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Commit '{sha}' not found in repository '{repository}'",
                        "code": "COMMIT_NOT_FOUND"
                    }
                )
            elif e.status == 422:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Invalid commit SHA: {sha}",
                        "code": "INVALID_SHA"
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
