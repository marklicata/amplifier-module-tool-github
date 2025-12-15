"""Create a new repository."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import (
    RateLimitError,
    PermissionError,
    ValidationError,
    GitHubError,
)

try:
    from github.GithubException import GithubException
except ImportError:
    GithubException = Exception


class CreateRepositoryTool(GitHubBaseTool):
    """Tool to create a new GitHub repository."""

    @property
    def name(self) -> str:
        return "github_create_repository"

    @property
    def description(self) -> str:
        return (
            "Create a new repository on GitHub. Can create repositories for the authenticated user "
            "or for an organization (if user has permission). Supports setting visibility, "
            "initialization with README, .gitignore, and license."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Repository name (required)"
                },
                "description": {
                    "type": "string",
                    "description": "Repository description"
                },
                "private": {
                    "type": "boolean",
                    "description": "Create as private repository (default: false)",
                    "default": False
                },
                "organization": {
                    "type": "string",
                    "description": "Organization name (if creating for an organization)"
                },
                "auto_init": {
                    "type": "boolean",
                    "description": "Initialize with README.md (default: false)",
                    "default": False
                },
                "gitignore_template": {
                    "type": "string",
                    "description": "gitignore template to use (e.g., 'Python', 'Node', 'Java')"
                },
                "license_template": {
                    "type": "string",
                    "description": "License template to use (e.g., 'mit', 'apache-2.0', 'gpl-3.0')"
                },
                "allow_squash_merge": {
                    "type": "boolean",
                    "description": "Allow squash merging (default: true)",
                    "default": True
                },
                "allow_merge_commit": {
                    "type": "boolean",
                    "description": "Allow merge commits (default: true)",
                    "default": True
                },
                "allow_rebase_merge": {
                    "type": "boolean",
                    "description": "Allow rebase merging (default: true)",
                    "default": True
                },
                "delete_branch_on_merge": {
                    "type": "boolean",
                    "description": "Automatically delete branches after merge (default: false)",
                    "default": False
                },
                "has_issues": {
                    "type": "boolean",
                    "description": "Enable issues (default: true)",
                    "default": True
                },
                "has_projects": {
                    "type": "boolean",
                    "description": "Enable projects (default: true)",
                    "default": True
                },
                "has_wiki": {
                    "type": "boolean",
                    "description": "Enable wiki (default: true)",
                    "default": True
                }
            },
            "required": ["name"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Create a new repository."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        name = input_data.get("name")
        description = input_data.get("description")
        private = input_data.get("private", False)
        organization = input_data.get("organization")
        auto_init = input_data.get("auto_init", False)
        gitignore_template = input_data.get("gitignore_template")
        license_template = input_data.get("license_template")
        allow_squash_merge = input_data.get("allow_squash_merge", True)
        allow_merge_commit = input_data.get("allow_merge_commit", True)
        allow_rebase_merge = input_data.get("allow_rebase_merge", True)
        delete_branch_on_merge = input_data.get("delete_branch_on_merge", False)
        has_issues = input_data.get("has_issues", True)
        has_projects = input_data.get("has_projects", True)
        has_wiki = input_data.get("has_wiki", True)

        if not name:
            return ToolResult(
                success=False,
                error={"message": "name parameter is required", "code": "MISSING_PARAMETER"}
            )

        if not name.strip():
            return ToolResult(
                success=False,
                error=ValidationError("Repository name cannot be empty").to_dict()
            )

        try:
            # Prepare repository creation parameters
            repo_kwargs = {
                "name": name,
                "private": private,
                "auto_init": auto_init,
                "allow_squash_merge": allow_squash_merge,
                "allow_merge_commit": allow_merge_commit,
                "allow_rebase_merge": allow_rebase_merge,
                "delete_branch_on_merge": delete_branch_on_merge,
                "has_issues": has_issues,
                "has_projects": has_projects,
                "has_wiki": has_wiki,
            }

            if description:
                repo_kwargs["description"] = description
            if gitignore_template:
                repo_kwargs["gitignore_template"] = gitignore_template
            if license_template:
                repo_kwargs["license_template"] = license_template

            # Create repository for organization or user
            if organization:
                org = self.manager.client.get_organization(organization)
                repo = org.create_repo(**repo_kwargs)
                owner_type = "organization"
            else:
                user = self.manager.github_user
                repo = user.create_repo(**repo_kwargs)
                owner_type = "user"

            return ToolResult(
                success=True,
                output={
                    "repository": {
                        "id": repo.id,
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description,
                        "private": repo.private,
                        "owner": repo.owner.login,
                        "owner_type": owner_type,
                        "url": repo.html_url,
                        "clone_url": repo.clone_url,
                        "ssh_url": repo.ssh_url,
                        "default_branch": repo.default_branch,
                        "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    },
                    "message": f"Repository '{repo.full_name}' created successfully"
                }
            )

        except GithubException as e:
            if e.status == 403:
                return ToolResult(
                    success=False,
                    error=PermissionError("create repository").to_dict()
                )
            elif e.status == 404:
                return ToolResult(
                    success=False,
                    error={
                        "message": f"Organization '{organization}' not found",
                        "code": "ORGANIZATION_NOT_FOUND"
                    }
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
