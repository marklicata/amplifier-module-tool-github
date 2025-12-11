# Repository setup required :wave:
    
Please visit the website URL :point_right: for this repository to complete the setup of this repository and configure access controls.
# Amplifier Module: GitHub Integration

This module provides GitHub API integration capabilities as tools for Amplifier LLM agents. It enables interaction with GitHub repositories, issues, pull requests, and other GitHub features through PyGithub.

## Status

**Version:** 0.1.0 (V1)  
**Implementation Status:** Issues only (fully implemented)

### V1 Features (Current)
- ✅ **Issues Management**: Full CRUD operations
  - List issues with filtering
  - Get issue details
  - Create new issues
  - Update existing issues
  - Add comments to issues

### Future Features (TODO)
- 🔲 **Pull Requests**: Create, review, merge PRs
- 🔲 **Repositories**: Browse, create, manage repos
- 🔲 **Commits**: View commit history and details
- 🔲 **Branches**: List, create, manage branches
- 🔲 **Releases**: View and create releases
- 🔲 **Actions/Workflows**: Trigger and monitor workflows
- 🔲 **Projects**: Manage GitHub Projects
- 🔲 **Code Search**: Search across repositories
- 🔲 **Security**: Dependabot alerts, security advisories

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

### `github_list_issues`
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
    ├── issues/          # Issue management tools (v1.0)
    │   ├── list.py      # List issues
    │   ├── get.py       # Get issue details
    │   ├── create.py    # Create issue
    │   ├── update.py    # Update issue
    │   └── comment.py   # Comment on issue
    ├── pull_requests/   # TODO: v1.1
    ├── repositories/    # TODO: v1.2
    ├── commits/         # TODO: v1.3
    ├── branches/        # TODO: v1.3
    ├── releases/        # TODO: v1.4
    └── actions/         # TODO: v1.5
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
