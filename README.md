# Repository setup required :wave:
    
Please visit the website URL :point_right: for this repository to complete the setup of this repository and configure access controls.
# Amplifier Module: GitHub Integration

This module provides GitHub API integration capabilities as tools for Amplifier LLM agents. It enables interaction with GitHub repositories, issues, pull requests, and other GitHub features through PyGithub.

## Status

**Version:** 1.5.0  
**Implementation Status:** Fully implemented (34 tools)

### Implemented Features
- ✅ **Issues Management** (5 tools): Full CRUD operations
- ✅ **Pull Requests** (6 tools): Create, review, merge PRs
- ✅ **Repositories** (5 tools): Browse, create, manage repos, get file contents
- ✅ **Commits** (2 tools): View commit history and details
- ✅ **Branches** (4 tools): List, create, compare branches
- ✅ **Releases & Tags** (5 tools): Manage releases and tags
- ✅ **Actions/Workflows** (7 tools): Trigger and monitor workflows

### Future Features (TODO)
- 🔲 **Projects**: Manage GitHub Projects
- 🔲 **Code Search**: Search across repositories
- 🔲 **Security**: Dependabot alerts, security advisories
- 🔲 **Advanced Repository**: Webhooks, deploy keys, collaborators
- 🔲 **Discussions**: Create and manage discussions

## Installation

```bash
pip install amplifier-module-tool-github
```

Or with uv:

```bash
uv pip install amplifier-module-tool-github
```

## Configuration

The module requires a GitHub token for authentication. You can use either:
- Personal Access Token (Classic or Fine-grained)
- GitHub App installation token

### Example Configuration

```python
config = {
    "token": "ghp_your_personal_access_token",  # Required
    "base_url": "https://api.github.com"        # Optional (for GitHub Enterprise)
}
```

### Token Permissions

For the V1 issue management features, your token needs:
- `repo` scope (for private repos) or `public_repo` (for public repos only)
- Read and write access to issues

## Tools Provided

### Issues (5 tools)

#### `github_list_issues`
List issues in a GitHub repository with filtering options.

**Parameters:**
- `repository` (string, required): Repository name in `owner/repo` format
- `state` (string, optional): Filter by state (`open`, `closed`, `all`). Default: `open`
- `labels` (array, optional): Filter by labels
- `assignee` (string, optional): Filter by assignee username
- `creator` (string, optional): Filter by creator username
- `mentioned` (string, optional): Filter by mentioned username
- `sort` (string, optional): Sort by (`created`, `updated`, `comments`). Default: `created`
- `direction` (string, optional): Sort direction (`asc`, `desc`). Default: `desc`
- `limit` (integer, optional): Max results (1-100). Default: 30

**Example:**
```json
{
  "repository": "microsoft/vscode",
  "state": "open",
  "labels": ["bug", "verified"],
  "limit": 10
}
```

### `github_get_issue`
Get detailed information about a specific issue.

**Parameters:**
- `repository` (string, required): Repository name in `owner/repo` format
- `issue_number` (integer, required): Issue number
- `include_comments` (boolean, optional): Include comments. Default: `false`
- `comments_limit` (integer, optional): Max comments to return (1-100). Default: 10

**Example:**
```json
{
  "repository": "microsoft/vscode",
  "issue_number": 12345,
  "include_comments": true
}
```

### `github_create_issue`
Create a new issue in a repository.

**Parameters:**
- `repository` (string, required): Repository name in `owner/repo` format
- `title` (string, required): Issue title
- `body` (string, optional): Issue description (Markdown supported)
- `labels` (array, optional): Labels to add
- `assignees` (array, optional): Usernames to assign
- `milestone` (integer, optional): Milestone number

**Example:**
```json
{
  "repository": "microsoft/vscode",
  "title": "Feature request: Dark mode improvements",
  "body": "It would be great if...",
  "labels": ["feature-request"],
  "assignees": ["username"]
}
```

### `github_update_issue`
Update an existing issue. Only include fields you want to change.

**Parameters:**
- `repository` (string, required): Repository name in `owner/repo` format
- `issue_number` (integer, required): Issue number
- `title` (string, optional): New title
- `body` (string, optional): New description
- `state` (string, optional): New state (`open`, `closed`)
- `labels` (array, optional): Labels to set (replaces existing)
- `assignees` (array, optional): Assignees to set (replaces existing)
- `milestone` (integer, optional): Milestone number (0 to remove)

**Example:**
```json
{
  "repository": "microsoft/vscode",
  "issue_number": 12345,
  "state": "closed",
  "labels": ["bug", "fixed"]
}
```

### `github_comment_issue`
Add a comment to an issue.

**Parameters:**
- `repository` (string, required): Repository name in `owner/repo` format
- `issue_number` (integer, required): Issue number
- `body` (string, required): Comment text (Markdown supported)

**Example:**
```json
{
  "repository": "microsoft/vscode",
  "issue_number": 12345,
  "body": "This has been fixed in the latest release!"
}
```

### Pull Requests (6 tools)

- `github_list_pull_requests` - List PRs with filtering by state, labels, author
- `github_get_pull_request` - Get PR details including files changed, reviews, and status checks
- `github_create_pull_request` - Create new PR with reviewers and labels
- `github_update_pull_request` - Update PR title, body, state, reviewers
- `github_merge_pull_request` - Merge PR with different strategies (merge, squash, rebase)
- `github_review_pull_request` - Submit PR review (approve, request changes, comment)

### Repositories (5 tools)

- `github_get_repository` - Get repository details, stats, and settings
- `github_list_repositories` - List repositories for user or organization
- `github_create_repository` - Create new repository with initialization options
- `github_get_file_content` - Get file content from repository (supports refs)
- `github_list_repository_contents` - List directory contents (with recursive option)

### Commits (2 tools)

- `github_list_commits` - List commits with filtering by author, path, date range
- `github_get_commit` - Get commit details including files changed and stats

### Branches (4 tools)

- `github_list_branches` - List all branches with protection status
- `github_get_branch` - Get branch details including protection rules
- `github_create_branch` - Create new branch from specific ref
- `github_compare_branches` - Compare two branches showing diff and commits

### Releases & Tags (5 tools)

- `github_list_releases` - List releases with assets and download counts
- `github_get_release` - Get release details by ID or tag name
- `github_create_release` - Create new release with draft/prerelease options
- `github_list_tags` - List all repository tags
- `github_create_tag` - Create lightweight or annotated tag

### Actions & Workflows (7 tools)

- `github_list_workflows` - List all workflows in repository
- `github_get_workflow` - Get workflow details
- `github_trigger_workflow` - Manually trigger workflow with inputs
- `github_list_workflow_runs` - List workflow runs with filtering
- `github_get_workflow_run` - Get run details including jobs and steps
- `github_cancel_workflow_run` - Cancel running workflow
- `github_rerun_workflow` - Rerun workflow (all jobs or failed jobs only)

## Usage with Amplifier

```python
from amplifier_core import Amplifier
from amplifier_module_tool_github import mount

# Initialize Amplifier
amplifier = Amplifier()

# Mount the GitHub module
config = {
    "token": "your_github_token"
}
await amplifier.mount_module(mount, config)
```

## Error Handling

The module includes comprehensive error handling:

- `AuthenticationError`: Invalid or missing GitHub token
- `RepositoryNotFoundError`: Repository doesn't exist or not accessible
- `IssueNotFoundError`: Issue doesn't exist
- `RateLimitError`: GitHub API rate limit exceeded
- `PermissionError`: Insufficient permissions for operation
- `ValidationError`: Invalid input parameters

## Rate Limits

GitHub API has rate limits:
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour

The module will return a `RateLimitError` when limits are exceeded, including the reset time.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Coverage

```bash
pytest --cov=amplifier_module_tool_github tests/
```

## Dependencies

- `amplifier-core`: Core Amplifier framework
- `PyGithub>=2.1.0`: Python library for GitHub API

## Architecture

The module follows the standard Amplifier module pattern with organized tool categories:

```
amplifier_module_tool_github/
├── __init__.py          # Module entry point and mount function
├── manager.py           # GitHubManager - handles API client lifecycle
├── exceptions.py        # Custom exception classes
└── tools/
    ├── __init__.py      # Tool exports
    ├── base.py          # GitHubBaseTool - base class for all tools
    ├── issues/          # Issue management (5 tools)
    ├── pull_requests/   # PR management (6 tools)
    ├── repositories/    # Repository management (5 tools)
    ├── commits/         # Commit tools (2 tools)
    ├── branches/        # Branch management (4 tools)
    ├── releases/        # Release and tag management (5 tools)
    └── actions/         # Workflow and Actions tools (7 tools)
```

## Contributing

Contributions are welcome! Future areas for expansion:

1. **Pull Requests**: Full PR lifecycle management
2. **Repositories**: Repository creation and configuration
3. **Actions**: Workflow triggering and monitoring
4. **Code Search**: Search across repositories
5. **Security**: Dependabot and security advisory integration

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/microsoft/amplifier-module-tool-github/issues
- Documentation: https://github.com/microsoft/amplifier

## Related Modules

- [amplifier-module-tool-astred](https://github.com/microsoft/amplifier-module-tool-astred) - Code analysis with Astred
- [amplifier-module-tool-codeql](https://github.com/microsoft/amplifier-module-tool-codeql) - Security analysis with CodeQL
