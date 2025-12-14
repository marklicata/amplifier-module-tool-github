"""List issues in a repository."""

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


class ListIssuesTool(GitHubBaseTool):
    """Tool to list issues in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_list_issues"

    @property
    def description(self) -> str:
        return (
            "List issues in a GitHub repository. Returns a list of issues with their "
            "basic information including number, title, state, author, labels, and dates. "
            "Supports filtering by state (open/closed/all), labels, assignee, and more."
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
                    "description": "Filter by issue state (default: open)",
                    "default": "open"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by labels (must have all specified labels)"
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter by assignee username (use 'none' for unassigned, '*' for any assigned)"
                },
                "creator": {
                    "type": "string",
                    "description": "Filter by issue creator username"
                },
                "mentioned": {
                    "type": "string",
                    "description": "Filter by username mentioned in the issue"
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "comments"],
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
                    "description": "Maximum number of issues to return (default: 30, max: 100)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": []
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """List issues in a repository or across all configured repositories."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        state = input_data.get("state", "open")
        labels = input_data.get("labels", [])
        assignee = input_data.get("assignee")
        creator = input_data.get("creator")
        mentioned = input_data.get("mentioned")
        sort = input_data.get("sort", "created")
        direction = input_data.get("direction", "desc")
        limit = input_data.get("limit", 30)
        
        # Note: @me translation is handled centrally in unified_tool.py before reaching this tool

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
            all_issues = []
            repo_errors = []
            
            # Query each repository
            for repo_name in repositories_to_query:
                try:
                    repo = self.manager.get_repository(repo_name)

                    # Get issues with filters
                    issues = repo.get_issues(
                        state=state,
                        labels=labels if labels else None,
                        assignee=assignee if assignee else None,
                        creator=creator if creator else None,
                        mentioned=mentioned if mentioned else None,
                        sort=sort,
                        direction=direction,
                    )

                    # Collect issue data
                    for issue in issues:
                        if len(all_issues) >= limit:
                            break
                        
                        # Skip pull requests (GitHub's API returns PRs as issues)
                        if issue.pull_request:
                            continue

                        issue_data = {
                            "repository": repo_name,
                            "number": issue.number,
                            "title": issue.title,
                            "state": issue.state,
                            "author": issue.user.login if issue.user else None,
                            "created_at": issue.created_at.isoformat() if issue.created_at else None,
                            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                            "labels": [label.name for label in issue.labels],
                            "assignees": [assignee.login for assignee in issue.assignees],
                            "comments": issue.comments,
                            "url": issue.html_url,
                        }
                        all_issues.append(issue_data)
                        
                    if len(all_issues) >= limit:
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
                    "count": len(all_issues),
                    "issues": all_issues,
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
            error_msg = str(e) if str(e) else repr(e)
            return ToolResult(
                success=False,
                error={
                    "message": f"Unexpected error: {error_msg}",
                    "code": "UNEXPECTED_ERROR",
                    "type": type(e).__name__
                }
            )
