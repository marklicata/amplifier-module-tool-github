"""GitHub tool implementations."""

from .base import GitHubBaseTool

# Issue management tools (v1.0 - implemented)
from .issues import (
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
)

# TODO: Future tool categories
# from .pull_requests import (...)  # v1.1
# from .repositories import (...)   # v1.2
# from .commits import (...)        # v1.3
# from .branches import (...)       # v1.3
# from .releases import (...)       # v1.4
# from .actions import (...)        # v1.5

__all__ = [
    "GitHubBaseTool",
    # Issues
    "ListIssuesTool",
    "GetIssueTool",
    "CreateIssueTool",
    "UpdateIssueTool",
    "CommentIssueTool",
]
