"""List pull requests in a repository."""

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


class ListPullRequestsTool(GitHubBaseTool):
    """Tool to list pull requests in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_pull_requests"

    @property
    def description(self) -> str:
        return (
            "List pull requests in a GitHub repository. Returns a list of PRs with their "
            "basic information including number, title, state, author, labels, and dates. "
            "Supports filtering by state (open/closed/all), labels, and sorting options. "
            "Includes draft PRs in results."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": (
                        "Full repository name in format 'owner/repo' (e.g., 'microsoft/vscode'). "
                        "Optional if repositories are configured - will search across all configured repositories. "
                        "If provided, searches only this specific repository."
                    )
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "Filter by PR state (default: open)",
                    "default": "open"
                },
                "head": {
                    "type": "string",
                    "description": "Filter by head branch (format: 'user:branch')"
                },
                "base": {
                    "type": "string",
                    "description": "Filter by base branch"
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "popularity", "long-running"],
                    "description": "Sort field (default: created)",
                    "default": "created"
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort direction (default: desc)",
                    "default": "desc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of PRs to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": []
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List pull requests in a repository or across all configured repositories."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        state = input_data.get("state", "open")
        head = input_data.get("head")
        base = input_data.get("base")
        sort = input_data.get("sort", "created")
        direction = input_data.get("direction", "desc")
        limit = input_data.get("limit", 30)

        # Determine which repositories to query
        if repository:
            # Single repository specified
            access_error = self._check_repository_access(repository)
            if access_error:
                return access_error
            repositories_to_query = [repository]
        else:
            # No repository specified - check if we have configured repos
            configured_repos = self.manager.get_configured_repositories()
            if not configured_repos:
                return ToolResult(
                    success=False,
                    error={
                        "message": "No repository specified and no repositories configured. "
                                   "Either provide a 'repository' parameter or configure repositories in settings.",
                        "code": "MISSING_REPOSITORY"
                    }
                )
            repositories_to_query = configured_repos

        try:
            all_prs = []
            repo_errors = []
            
            # Query each repository
            for repo_name in repositories_to_query:
                try:
                    repo = self.manager.get_repository(repo_name)

                    # Get pull requests with filters
                    pulls = repo.get_pulls(
                        state=state,
                        sort=sort,
                        direction=direction,
                        base=base if base else None,
                        head=head if head else None,
                    )

                    # Collect PR data
                    for pr in pulls:
                        if len(all_prs) >= limit:
                            break

                        pr_data = {
                            "repository": repo_name,
                            "number": pr.number,
                            "title": pr.title,
                            "state": pr.state,
                            "draft": pr.draft,
                            "author": pr.user.login if pr.user else None,
                            "created_at": pr.created_at.isoformat() if pr.created_at else None,
                            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                            "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                            "merged": pr.merged,
                            "mergeable": pr.mergeable,
                            "labels": [label.name for label in pr.labels],
                            "assignees": [assignee.login for assignee in pr.assignees],
                            "reviewers": [reviewer.login for reviewer in pr.requested_reviewers],
                            "head": {
                                "ref": pr.head.ref,
                                "sha": pr.head.sha,
                            },
                            "base": {
                                "ref": pr.base.ref,
                                "sha": pr.base.sha,
                            },
                            "comments": pr.comments,
                            "review_comments": pr.review_comments,
                            "commits": pr.commits,
                            "additions": pr.additions,
                            "deletions": pr.deletions,
                            "changed_files": pr.changed_files,
                            "url": pr.html_url,
                        }
                        all_prs.append(pr_data)
                        
                    if len(all_prs) >= limit:
                        break
                        
                except (RepositoryNotFoundError, GithubException) as e:
                    # Track errors but continue with other repos
                    repo_errors.append({
                        "repository": repo_name,
                        "error": str(e)
                    })
                    continue

            return ToolResult(
                success=True,
                output={
                    "repositories_queried": repositories_to_query,
                    "state": state,
                    "count": len(all_prs),
                    "pull_requests": all_prs,
                    "errors": repo_errors if repo_errors else None,
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
