"""Review a pull request."""

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


class ReviewPullRequestTool(GitHubBaseTool):
    """Tool to review a pull request."""

    @property
    def name(self) -> str:
        return "github_review_pull_request"

    @property
    def description(self) -> str:
        return (
            "Submit a review for a pull request. Can approve, request changes, or comment. "
            "Can include inline comments on specific lines of code. Requires write access."
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
                "event": {
                    "type": "string",
                    "enum": ["APPROVE", "REQUEST_CHANGES", "COMMENT"],
                    "description": "Review action: APPROVE, REQUEST_CHANGES, or COMMENT (required)"
                },
                "body": {
                    "type": "string",
                    "description": "Review comment body (required for REQUEST_CHANGES and COMMENT)"
                },
                "comments": {
                    "type": "array",
                    "description": "Inline comments on specific lines of code",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to comment on"
                            },
                            "position": {
                                "type": "integer",
                                "description": "Position in the diff to comment on (deprecated, use line)"
                            },
                            "line": {
                                "type": "integer",
                                "description": "Line number in the file to comment on"
                            },
                            "side": {
                                "type": "string",
                                "enum": ["LEFT", "RIGHT"],
                                "description": "Side of the diff (LEFT for deletion, RIGHT for addition)"
                            },
                            "body": {
                                "type": "string",
                                "description": "Comment body"
                            }
                        },
                        "required": ["path", "body"]
                    }
                }
            },
            "required": ["repository", "pull_number", "event"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Review a pull request."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        pull_number = input_data.get("pull_number")
        event = input_data.get("event")
        body = input_data.get("body", "")
        comments = input_data.get("comments", [])

        if not repository or pull_number is None or not event:
            return ToolResult(
                success=False,
                error={
                    "message": "repository, pull_number, and event parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        # Validate that body is provided for REQUEST_CHANGES and COMMENT
        if event in ["REQUEST_CHANGES", "COMMENT"] and not body.strip():
            return ToolResult(
                success=False,
                error=ValidationError(
                    f"body is required when event is {event}"
                ).to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)
            pr = repo.get_pull(pull_number)

            # Check if PR is open
            if pr.state != "open":
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Pull request #{pull_number} is not open",
                        "code": "PR_NOT_OPEN"
                    }
                )

            # Prepare review comments
            review_comments = []
            if comments:
                # Get the latest commit SHA
                last_commit = pr.get_commits().reversed[0]
                commit_sha = last_commit.sha

                for comment in comments:
                    review_comment = {
                        "path": comment["path"],
                        "body": comment["body"],
                    }
                    # Use line if provided, otherwise use position
                    if "line" in comment:
                        review_comment["line"] = comment["line"]
                        review_comment["side"] = comment.get("side", "RIGHT")
                    elif "position" in comment:
                        review_comment["position"] = comment["position"]
                    
                    review_comments.append(review_comment)

            # Create the review
            review_kwargs = {
                "event": event,
            }
            if body:
                review_kwargs["body"] = body
            if review_comments:
                review_kwargs["comments"] = review_comments

            review = pr.create_review(**review_kwargs)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "pull_request": {
                        "number": pr.number,
                        "title": pr.title,
                    },
                    "review": {
                        "id": review.id,
                        "user": review.user.login if review.user else None,
                        "state": review.state,
                        "body": review.body,
                        "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None,
                    },
                    "message": f"Review submitted successfully for PR #{pr.number}"
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
            elif e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("review pull request").to_dict()
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
