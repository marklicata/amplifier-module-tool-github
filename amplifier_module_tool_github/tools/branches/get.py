"""Get branch details."""

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


class GetBranchTool(GitHubBaseTool):
    """Tool to get detailed information about a specific branch."""

    @property
    def name(self) -> str:
        return "github_get_branch"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific branch in a GitHub repository. "
            "Returns branch metadata, latest commit information, and protection rules if applicable."
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
                "branch": {
                    "type": "string",
                    "description": "Branch name (required)"
                }
            },
            "required": ["repository", "branch"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Get branch details."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        branch_name = input_data.get("branch")

        if not repository or not branch_name:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and branch parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        try:
            repo = self.manager.get_repository(repository)
            branch = repo.get_branch(branch_name)

            branch_data = {
                "name": branch.name,
                "sha": branch.commit.sha,
                "protected": branch.protected,
                "commit": {
                    "sha": branch.commit.sha,
                    "message": branch.commit.commit.message if branch.commit.commit else None,
                    "author": {
                        "name": branch.commit.commit.author.name if branch.commit.commit and branch.commit.commit.author else None,
                        "email": branch.commit.commit.author.email if branch.commit.commit and branch.commit.commit.author else None,
                        "date": branch.commit.commit.author.date.isoformat() if branch.commit.commit and branch.commit.commit.author and branch.commit.commit.author.date else None,
                    },
                    "url": branch.commit.html_url if hasattr(branch.commit, 'html_url') else None,
                },
            }

            # Get protection rules if branch is protected
            if branch.protected:
                try:
                    protection = branch.get_protection()
                    protection_data = {
                        "enabled": True,
                    }

                    # Required status checks
                    try:
                        status_checks = protection.required_status_checks
                        if status_checks:
                            protection_data["required_status_checks"] = {
                                "strict": status_checks.strict,
                                "contexts": status_checks.contexts,
                            }
                    except Exception:
                        pass

                    # Required pull request reviews
                    try:
                        pr_reviews = protection.required_pull_request_reviews
                        if pr_reviews:
                            protection_data["required_pull_request_reviews"] = {
                                "dismissal_restrictions": bool(pr_reviews.dismissal_restrictions),
                                "dismiss_stale_reviews": pr_reviews.dismiss_stale_reviews,
                                "require_code_owner_reviews": pr_reviews.require_code_owner_reviews,
                                "required_approving_review_count": pr_reviews.required_approving_review_count,
                            }
                    except Exception:
                        pass

                    # Enforce admins
                    try:
                        protection_data["enforce_admins"] = protection.enforce_admins.enabled if protection.enforce_admins else False
                    except Exception:
                        pass

                    # Restrictions
                    try:
                        restrictions = protection.restrictions
                        if restrictions:
                            protection_data["restrictions"] = {
                                "users": [user.login for user in restrictions.users] if restrictions.users else [],
                                "teams": [team.slug for team in restrictions.teams] if restrictions.teams else [],
                            }
                    except Exception:
                        pass

                    branch_data["protection"] = protection_data
                except Exception:
                    branch_data["protection"] = {"enabled": True, "details_unavailable": True}
            else:
                branch_data["protection"] = {"enabled": False}

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "branch": branch_data,
                }
            )

        except GithubException as e:
            if e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Branch '{branch_name}' not found in repository '{repository}'",
                        "code": "BRANCH_NOT_FOUND"
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
