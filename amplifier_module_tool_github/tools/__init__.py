"""GitHub tool implementations."""

from .base import GitHubBaseTool

# Issue management tools (v1.0)
from .issues import (
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
)

# Pull request management tools (v1.1)
from .pull_requests import (
    ListPullRequestsTool,
    GetPullRequestTool,
    CreatePullRequestTool,
    UpdatePullRequestTool,
    MergePullRequestTool,
    ReviewPullRequestTool,
)

# Repository management tools (v1.2)
from .repositories import (
    GetRepositoryTool,
    ListRepositoriesTool,
    CreateRepositoryTool,
    GetFileContentTool,
    ListRepositoryContentsTool,
)

# Commit management tools (v1.3)
from .commits import (
    ListCommitsTool,
    GetCommitTool,
)

# Branch management tools (v1.3)
from .branches import (
    ListBranchesTool,
    GetBranchTool,
    CreateBranchTool,
    CompareBranchesTool,
)

# Release and tag management tools (v1.4)
from .releases import (
    ListReleasesTool,
    GetReleaseTool,
    CreateReleaseTool,
    ListTagsTool,
    CreateTagTool,
)

# GitHub Actions and workflow tools (v1.5)
from .actions import (
    ListWorkflowsTool,
    GetWorkflowTool,
    TriggerWorkflowTool,
    ListWorkflowRunsTool,
    GetWorkflowRunTool,
    CancelWorkflowRunTool,
    RerunWorkflowTool,
)

__all__ = [
    "GitHubBaseTool",
    # Issues
    "ListIssuesTool",
    "GetIssueTool",
    "CreateIssueTool",
    "UpdateIssueTool",
    "CommentIssueTool",
    # Pull Requests
    "ListPullRequestsTool",
    "GetPullRequestTool",
    "CreatePullRequestTool",
    "UpdatePullRequestTool",
    "MergePullRequestTool",
    "ReviewPullRequestTool",
    # Repositories
    "GetRepositoryTool",
    "ListRepositoriesTool",
    "CreateRepositoryTool",
    "GetFileContentTool",
    "ListRepositoryContentsTool",
    # Commits
    "ListCommitsTool",
    "GetCommitTool",
    # Branches
    "ListBranchesTool",
    "GetBranchTool",
    "CreateBranchTool",
    "CompareBranchesTool",
    # Releases
    "ListReleasesTool",
    "GetReleaseTool",
    "CreateReleaseTool",
    "ListTagsTool",
    "CreateTagTool",
    # Actions
    "ListWorkflowsTool",
    "GetWorkflowTool",
    "TriggerWorkflowTool",
    "ListWorkflowRunsTool",
    "GetWorkflowRunTool",
    "CancelWorkflowRunTool",
    "RerunWorkflowTool",
]
