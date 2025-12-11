"""Get details of a pull request."""

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


class GetPullRequestTool(GitHubBaseTool):
    """Tool to get detailed information about a pull request."""

    @property
    def name(self) -> str:
        return "github_get_pull_request"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific pull request in a GitHub repository. "
            "Includes PR metadata, files changed, review comments, and status checks."
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
                "pull_number": {
                    "type": "integer",
                    "description": "Pull request number"
                },
                "include_files": {
                    "type": "boolean",
                    "description": "Include list of files changed (default: true)",
                    "default": True
                },
                "include_reviews": {
                    "type": "boolean",
                    "description": "Include review comments (default: true)",
                    "default": True
                },
                "include_commits": {
                    "type": "boolean",
                    "description": "Include list of commits (default: false)",
                    "default": False
                }
            },
            "required": ["repository", "pull_number"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get pull request details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        pull_number = input_data.get("pull_number")
        include_files = input_data.get("include_files", True)
        include_reviews = input_data.get("include_reviews", True)
        include_commits = input_data.get("include_commits", False)

        if not repository or pull_number is None:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and pull_number parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            pr = repo.get_pull(pull_number)

            pr_data = {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "draft": pr.draft,
                "author": pr.user.login if pr.user else None,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "merged": pr.merged,
                "merged_by": pr.merged_by.login if pr.merged_by else None,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "labels": [label.name for label in pr.labels],
                "assignees": [assignee.login for assignee in pr.assignees],
                "reviewers": [reviewer.login for reviewer in pr.requested_reviewers],
                "head": {
                    "ref": pr.head.ref,
                    "sha": pr.head.sha,
                    "repo": pr.head.repo.full_name if pr.head.repo else None,
                },
                "base": {
                    "ref": pr.base.ref,
                    "sha": pr.base.sha,
                    "repo": pr.base.repo.full_name if pr.base.repo else None,
                },
                "comments": pr.comments,
                "review_comments": pr.review_comments,
                "commits": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "url": pr.html_url,
            }

            # Include files changed if requested
            if include_files:
                files = []
                for file in pr.get_files():
                    files.append({
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                        "patch": file.patch if hasattr(file, 'patch') else None,
                    })
                pr_data["files"] = files

            # Include review comments if requested
            if include_reviews:
                reviews = []
                for review in pr.get_reviews():
                    reviews.append({
                        "id": review.id,
                        "user": review.user.login if review.user else None,
                        "body": review.body,
                        "state": review.state,
                        "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None,
                    })
                pr_data["reviews"] = reviews

                # Also include review comments (inline comments on code)
                review_comments = []
                for comment in pr.get_review_comments():
                    review_comments.append({
                        "id": comment.id,
                        "user": comment.user.login if comment.user else None,
                        "body": comment.body,
                        "path": comment.path,
                        "position": comment.position,
                        "line": comment.line if hasattr(comment, 'line') else None,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                    })
                pr_data["review_comments_details"] = review_comments

            # Include commits if requested
            if include_commits:
                commits = []
                for commit in pr.get_commits():
                    commits.append({
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": commit.commit.author.name if commit.commit.author else None,
                        "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None,
                    })
                pr_data["commits_list"] = commits

            # Get status checks
            try:
                last_commit = pr.get_commits().reversed[0]
                statuses = []
                for status in last_commit.get_statuses():
                    statuses.append({
                        "context": status.context,
                        "state": status.state,
                        "description": status.description,
                        "target_url": status.target_url,
                    })
                pr_data["status_checks"] = statuses
            except Exception:
                # Status checks might not be available
                pr_data["status_checks"] = []

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "pull_request": pr_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Pull request #{pull_number} not found in {repository}",
                        "code": "PR_NOT_FOUND"
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
