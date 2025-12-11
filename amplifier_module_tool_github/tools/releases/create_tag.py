"""Create a new tag."""

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


class CreateTagTool(GitHubBaseTool):
    """Tool to create a new tag in a GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_tag"

    @property
    def description(self) -> str:
        return (
            "Create a new tag in a GitHub repository. Can create lightweight tags "
            "or annotated tags with messages. Requires write access to the repository."
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
                "tag": {
                    "type": "string",
                    "description": "Tag name (required)"
                },
                "message": {
                    "type": "string",
                    "description": "Tag message (for annotated tags)"
                },
                "object_sha": {
                    "type": "string",
                    "description": "SHA of the object to tag (commit, tree, or blob). If not provided, tags HEAD of default branch"
                },
                "type": {
                    "type": "string",
                    "enum": ["commit", "tree", "blob"],
                    "description": "Type of object being tagged (default: commit)",
                    "default": "commit"
                },
                "tagger_name": {
                    "type": "string",
                    "description": "Name of the tagger (for annotated tags)"
                },
                "tagger_email": {
                    "type": "string",
                    "description": "Email of the tagger (for annotated tags)"
                }
            },
            "required": ["repository", "tag"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new tag."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        repository = input_data.get("repository")
        tag_name = input_data.get("tag")
        message = input_data.get("message")
        object_sha = input_data.get("object_sha")
        object_type = input_data.get("type", "commit")
        tagger_name = input_data.get("tagger_name")
        tagger_email = input_data.get("tagger_email")

        if not repository or not tag_name:
            return ToolResult(
                success=False,
                error={
                    "message": "repository and tag parameters are required",
                    "code": "MISSING_PARAMETER"
                }
            )

        if not tag_name.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Tag name cannot be empty").to_dict()
            )

        try:
            repo = self.manager.get_repository(repository)

            # Get the SHA to tag
            if not object_sha:
                # Default to HEAD of default branch
                default_branch = repo.get_branch(repo.default_branch)
                object_sha = default_branch.commit.sha

            # Create annotated tag if message is provided
            if message:
                # Get authenticated user info for tagger if not provided
                if not tagger_name or not tagger_email:
                    user = self.manager.github.get_user()
                    if not tagger_name:
                        tagger_name = user.name or user.login
                    if not tagger_email:
                        tagger_email = user.email or f"{user.login}@users.noreply.github.com"

                # Create tag object
                from datetime import datetime
                tag_obj = repo.create_git_tag(
                    tag=tag_name,
                    message=message,
                    object=object_sha,
                    type=object_type,
                    tagger={
                        "name": tagger_name,
                        "email": tagger_email,
                        "date": datetime.utcnow().isoformat() + "Z"
                    }
                )

                # Create reference to the tag
                ref = repo.create_git_ref(ref=f"refs/tags/{tag_name}", sha=tag_obj.sha)
                
                return ToolResult(
                    success=True,
                    output={
                        "repository": repository,
                        "tag": {
                            "name": tag_name,
                            "sha": tag_obj.sha,
                            "object_sha": object_sha,
                            "message": message,
                            "type": "annotated",
                            "ref": ref.ref,
                        },
                        "message": f"Annotated tag '{tag_name}' created successfully"
                    }
                )
            else:
                # Create lightweight tag (just a reference)
                ref = repo.create_git_ref(ref=f"refs/tags/{tag_name}", sha=object_sha)

                return ToolResult(
                    success=True,
                    output={
                        "repository": repository,
                        "tag": {
                            "name": tag_name,
                            "sha": object_sha,
                            "type": "lightweight",
                            "ref": ref.ref,
                        },
                        "message": f"Lightweight tag '{tag_name}' created successfully"
                    }
                )

        except GithubException as e:
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create tag").to_dict()
                )
            elif e.status == 422:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Tag '{tag_name}' already exists or validation error: {str(e)}",
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
