"""Create a new branch."""

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


class CreateBranchTool(GitHubBaseTool):
    """Tool to create a new branch in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_branch"

    @property
    def description(self) -> str:
        return (
            "Create a new branch in a GitHub repository. Can create from a specific commit SHA, "
            "branch name, or tag. Requires write access to the repository."
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
                    "description": "Name for the new branch (required)"
                },
                "from_ref": {
                    "type": "string",
                    "description": "Reference to create branch from (branch name, tag, or commit SHA). Defaults to repository's default branch"
                }
            },
            "required": ["repository", "branch"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new branch."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        branch_name = input_data.get("branch")
        from_ref = input_data.get("from_ref")

        if not repository or not branch_name:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and branch parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not branch_name.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Branch name cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get the SHA to create branch from
            if from_ref:
                # Try to get the ref (branch, tag, or commit)
                try:
                    # Try as a branch first
                    source_branch = repo.get_branch(from_ref)
                    source_sha = source_branch.commit.sha
                except GithubException:
                    try:
                        # Try as a commit
                        commit = repo.get_commit(from_ref)
                        source_sha = commit.sha
                    except GithubException:
                        return ToolResult(
                            success=False,
                            error={
                                "message": f"Reference '{from_ref}' not found",
                                "code": "REF_NOT_FOUND"
                            }
                        )
            else:
                # Use default branch
                default_branch = repo.get_branch(repo.default_branch)
                source_sha = default_branch.commit.sha
                from_ref = repo.default_branch

            # Create the new branch reference
            ref_name = f"refs/heads/{branch_name}"
            ref = repo.create_git_ref(ref=ref_name, sha=source_sha)

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    "branch": {
                        "name": branch_name,
                        "sha": source_sha,
                        "ref": ref.ref,
                        "created_from": from_ref,
                    },
                    "message": f"Branch '{branch_name}' created successfully from '{from_ref}'"
                }
            )

        except GithubException as e:
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create branch").to_dict()
                )
            elif e.status == 422:
                # Branch already exists or validation error
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Branch '{branch_name}' already exists or validation error: {str(e)}",
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
