"""List commits in a repository."""

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


class ListCommitsTool(GitHubBaseTool):
    """Tool to list commits in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_commits"

    @property
    def description(self) -> str:
        return (
            "List commits in a GitHub repository. Returns commit information including SHA, "
            "message, author, date, and stats. Supports filtering by author, path, date range, "
            "and branch/ref."
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
                    "description": "Branch name, tag, or commit SHA to start listing from (default: default branch)"
                },
                "path": {
                    "type": "string",
                    "description": "Only show commits that affected this file path"
                },
                "author": {
                    "type": "string",
                    "description": "GitHub username or email to filter by author"
                },
                "since": {
                    "type": "string",
                    "description": "Only commits after this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)"
                },
                "until": {
                    "type": "string",
                    "description": "Only commits before this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of commits to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List commits in a repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        sha = input_data.get("sha")
        path = input_data.get("path")
        author = input_data.get("author")
        since = input_data.get("since")
        until = input_data.get("until")
        limit = input_data.get("limit", 30)

        if not repository:
            return ToolResult(
                success=False,
                error={"message": "repository parameter is required", "code": "MISSING_PARAMETER"}
            )

        try:
            repo = self.manager.get_repository(repository)

            # Build kwargs for get_commits
            kwargs = {}
            if sha:
                kwargs["sha"] = sha
            if path:
                kwargs["path"] = path
            if author:
                kwargs["author"] = author
            if since:
                from datetime import datetime
                kwargs["since"] = datetime.fromisoformat(since.replace('Z', '+00:00'))
            if until:
                from datetime import datetime
                kwargs["until"] = datetime.fromisoformat(until.replace('Z', '+00:00'))

            commits = repo.get_commits(**kwargs)

            # Collect commit data
            commit_list = []
            count = 0
            for commit in commits:
                if count >= limit:
                    break

                commit_data = {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": {
                        "name": commit.commit.author.name if commit.commit.author else None,
                        "email": commit.commit.author.email if commit.commit.author else None,
                        "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None,
                        "username": commit.author.login if commit.author else None,
                    },
                    "committer": {
                        "name": commit.commit.committer.name if commit.commit.committer else None,
                        "email": commit.commit.committer.email if commit.commit.committer else None,
                        "date": commit.commit.committer.date.isoformat() if commit.commit.committer and commit.commit.committer.date else None,
                        "username": commit.committer.login if commit.committer else None,
                    },
                    "url": commit.html_url,
                    "comment_count": commit.commit.comment_count if hasattr(commit.commit, 'comment_count') else 0,
                }

                # Add stats if available
                try:
                    commit_data["stats"] = {
                        "additions": commit.stats.additions,
                        "deletions": commit.stats.deletions,
                        "total": commit.stats.total,
                    }
                except Exception:
                    pass

                # Add parent SHAs
                commit_data["parents"] = [parent.sha for parent in commit.parents]

                commit_list.append(commit_data)
                count += 1

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "sha": sha or repo.default_branch,
                    "count": len(commit_list),
                    "commits": commit_list,
                }
            )

        except RepositoryNotFoundError as e:
            return ToolResult(success=False, error=e.to_dict())

        except RateLimitError as e:
            return ToolResult(success=False, error=e.to_dict())

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Reference or path not found in repository '{repository}'",
                        "code": "NOT_FOUND"
                    }
                )
            return ToolResult(
                success=False,
                error={
                    "message": f"GitHub API error: {str(e)}",
                    "code": "GITHUB_API_ERROR"
                }
            )

        except ValueError as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Invalid date format: {str(e)}",
                    "code": "INVALID_DATE_FORMAT"
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
