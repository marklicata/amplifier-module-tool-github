# Repository setup required :wave:
    
Please visit the website URL :point_right: for this repository to complete the setup of this repository and configure access controls.
# Amplifier Module: GitHub Integration

This module provides GitHub API integration capabilities as tools for Amplifier LLM agents. It enables interaction with GitHub repositories, issues, pull requests, and other GitHub features through PyGithub.

## Status

**Version:** 1.5.0  
**Implementation Status:** Fully implemented (34 tools)  
**Test Coverage:** 225 tests, 100% passing ✅

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

## Documentation

For detailed information, see the [`/docs/`](docs/) directory:

- 📘 **[Configuration Guide](docs/CONFIGURATION.md)** - Detailed authentication and configuration options
- 🚀 **[Quick Start](QUICKSTART.md)** - Get up and running in minutes
- 🔧 **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and extending the module
- ✅ **[Test Coverage](docs/COMPREHENSIVE_TEST_COVERAGE.md)** - Complete test suite documentation (225 tests, 100% passing)
- 🔒 **[Security Policy](docs/SECURITY.md)** - Vulnerability reporting and security best practices
- 💬 **[Support Resources](docs/SUPPORT.md)** - Getting help and community resources
- 📋 **[Code of Conduct](docs/CODE_OF_CONDUCT.md)** - Community guidelines

## Installation

```bash
pip install amplifier-module-tool-github
```

Or with uv:

```bash
uv pip install amplifier-module-tool-github
```

## Configuration

Configuration is done through your `.amplifier/settings.yaml` file. See **[Configuration Guide](docs/CONFIGURATION.md)** for detailed examples and [`examples/settings.yaml.example`](examples/settings.yaml.example) for a template.

### Quick Start Configuration

Create or edit `.amplifier/settings.yaml`:

```yaml
modules:
  github:
    use_cli_auth: true        # Use GitHub CLI authentication
    prompt_if_missing: true   # Prompt if no auth found
    repositories: []          # Empty = allow all repos
```

### Authentication Methods

The module supports multiple authentication methods, tried in the following order:

1. **API Token (Explicit)** - Provide token directly in config
2. **Environment Variable** - Set `GITHUB_TOKEN` or `GH_TOKEN`
3. **GitHub CLI** - Use existing `gh auth login` credentials
4. **Interactive Prompt** - Fallback to user prompt if none of the above

### Example Configurations

#### Option 1: Direct Token Configuration
```yaml
# .amplifier/settings.yaml
modules:
  github:
    token: ghp_your_personal_access_token  # Explicit token
    base_url: https://api.github.com       # Optional (for GitHub Enterprise)
```

#### Option 2: Environment Variable
```bash
# Set in your environment
export GITHUB_TOKEN="ghp_your_personal_access_token"
# or
```

```yaml
# .amplifier/settings.yaml
modules:
  github:
    # Token will be read from environment automatically
    use_cli_auth: false  # Optional: disable CLI auth fallback
```
```

#### Option 3: GitHub CLI Authentication
```

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true  # Default: true, will use gh CLI token
```

#### Option 4: Interactive Prompt
```yaml
# .amplifier/settings.yaml
modules:
  github:
    prompt_if_missing: true   # Prompts on startup (default)
    # Or disable:
    # prompt_if_missing: false
```fig = {
    "prompt_if_missing": False  # Default: True, set False to disable prompting
}
```

### Configuration Options

- `token` (string, optional): GitHub personal access token or GitHub App token
- `use_cli_auth` (bool, optional): Enable GitHub CLI authentication. Default: `True`
You can restrict the tool to only work with specific repositories by providing a list of repository URLs or identifiers:

```yaml
# .amplifier/settings.yaml
modules:
  github:
    repositories:
      - https://github.com/microsoft/vscode
      - git@github.com:python/cpython.git
      - facebook/react  # Direct owner/repo format also works
``` "repositories": [
        "https://github.com/microsoft/vscode",
        "git@github.com:python/cpython.git",
        "facebook/react",  # Direct owner/repo format also works
    ]
}
```

**Supported formats:**
- HTTPS URLs: `https://github.com/owner/repo` or `https://github.com/owner/repo.git`
- SSH URLs: `git@github.com:owner/repo.git`
- Direct format: `owner/repo`
- GitHub Enterprise URLs (when `base_url` is configured)

When repositories are configured:
- All operations will only work with the specified repositories
- Attempting to access other repositories will result in a permission error
- Leave empty or omit to allow access to all repositories (default behavior)

### Token Permissions

Your token needs the following permissions:
- `repo` scope (for private repos) or `public_repo` (for public repos only)
- Read and write access to issues, pull requests, and other resources you want to manage

### Creating a Personal Access Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token" (classic)
3. Select required scopes: `repo` or `public_repo`
4. Copy the token and use it in your configuration

## Tool Overview

This module provides a **single unified tool** called `github` that supports **34 different operations**.

Instead of having 34 separate tools, all GitHub interactions go through one tool with an `operation` parameter that specifies what action to perform.

### Operation Types: User-Level vs Repository-Specific

Operations fall into two categories:

**Repository-Specific Operations** (Most operations)
- Can work across ALL configured repositories when no `repository` parameter is provided
- Or work within a single repository when `repository` parameter is specified
- Examples: `list_issues`, `list_pull_requests`
- If no repositories are configured and no repository parameter provided, an error is returned

**User-Level Operations**
- Work across your account or organization
- No repository parameter required
- Examples: `list_repositories`, `create_repository`

> **Tip**: Configure repositories in `.amplifier/settings.yaml` to enable cross-repository queries. For example, list all issues across your configured repos without specifying a repository parameter!

### Using the GitHub Tool

All operations follow this pattern:

```python
result = await amplifier.execute_tool(
    "github",  # Single tool name
    {
        "operation": "operation_name",  # What to do
        "parameters": {                  # Operation-specific params
            # ... parameters for this operation
        }
    }
)
```

### Available Operations (34 total)

The `operation` parameter accepts one of these values:

**Issues (5 operations)** - *All repository-specific*
- `list_issues` - List issues in a repository
- `get_issue` - Get detailed information about an issue
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue
- `comment_issue` - Add a comment to an issue

**Pull Requests (6 operations)** - *All repository-specific*
- `list_pull_requests` - List pull requests
- `get_pull_request` - Get PR details
- `create_pull_request` - Create a new PR
- `update_pull_request` - Update a PR
- `merge_pull_request` - Merge a PR
- `review_pull_request` - Submit a PR review

**Repositories (5 operations)** - *Mixed*
- `get_repository` - Get repository information [repo-specific]
- `list_repositories` - List repositories for user/org [user-level]
- `create_repository` - Create a new repository [user-level]
- `get_file_content` - Get file contents from a repository [repo-specific]
- `list_repository_contents` - List contents of a directory [repo-specific]

**Commits (2 operations)** - *All repository-specific*
- `list_commits` - List commits in a repository
- `get_commit` - Get detailed commit information

**Branches (4 operations)** - *All repository-specific*
- `list_branches` - List branches in a repository
- `get_branch` - Get branch information
- `create_branch` - Create a new branch
- `compare_branches` - Compare two branches

**Releases & Tags (5 operations)** - *All repository-specific*
- `list_releases` - List releases
- `get_release` - Get release details
- `create_release` - Create a new release
- `list_tags` - List repository tags
- `create_tag` - Create a new tag

**Actions/Workflows (7 operations)** - *All repository-specific*
- `list_workflows` - List GitHub Actions workflows
- `get_workflow` - Get workflow details
- `trigger_workflow` - Trigger a workflow run
- `list_workflow_runs` - List workflow runs
- `get_workflow_run` - Get workflow run details
- `cancel_workflow_run` - Cancel a running workflow
- `rerun_workflow` - Rerun a failed workflow

## Usage Examples

### Example 1: List Issues Across All Configured Repositories

```python
# With repositories configured in settings.yaml, query across all repos
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "list_issues",
        "parameters": {
            "state": "open",
            "assignee": "myusername",  # Find all issues assigned to me
            "limit": 50
        }
    }
)

# Output includes issues from all configured repositories
# Each issue includes "repository" field showing which repo it's from
```

### Example 2: List Issues in a Specific Repository

```python
# Query a single repository
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "list_issues",
        "parameters": {
            "repository": "microsoft/vscode",  # Specify exact repo
            "state": "open",
            "labels": ["bug", "verified"],
            "limit": 10
        }
    }
)
```

### Example 3: Create a Pull Request

```python
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "create_pull_request",
        "parameters": {
            "repository": "owner/repo",
            "title": "Add new feature",
            "body": "This PR adds...",
            "head": "feature-branch",
            "base": "main"
        }
    }
)
```

### Example 3: Get File Contents

```python
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "get_file_content",
        "parameters": {
            "repository": "owner/repo",
            "path": "src/main.py",
            "ref": "main"  # optional: branch/tag/commit
        }
    }
)

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

For detailed development information, see the **[Development Guide](docs/DEVELOPMENT.md)**.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest --cov=amplifier_module_tool_github tests/
```

**Test Status:** All 225 tests passing ✅ (100% pass rate)

See **[Test Coverage Documentation](docs/COMPREHENSIVE_TEST_COVERAGE.md)** for detailed test information.

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

Contributions are welcome! See the **[Development Guide](docs/DEVELOPMENT.md)** for setup instructions and coding guidelines.

Future areas for expansion:

1. **Projects**: GitHub Projects management
2. **Code Search**: Search across repositories
3. **Security**: Dependabot and security advisory integration
4. **Discussions**: Discussion management
5. **Advanced Repository**: Webhooks, deploy keys, collaborators

Please review our **[Code of Conduct](docs/CODE_OF_CONDUCT.md)** before contributing.

## License

MIT License - see LICENSE file for details.

## Support

For help and support:

- 📖 **[Support Resources](docs/SUPPORT.md)** - Comprehensive support guide
- 🐛 **GitHub Issues**: https://github.com/microsoft/amplifier-module-tool-github/issues
- 🔒 **[Security Issues](docs/SECURITY.md)** - Report vulnerabilities privately
- 💬 **Documentation**: https://github.com/microsoft/amplifier

## Related Modules

- [amplifier-module-tool-astred](https://github.com/microsoft/amplifier-module-tool-astred) - Code analysis with Astred
- [amplifier-module-tool-codeql](https://github.com/microsoft/amplifier-module-tool-codeql) - Security analysis with CodeQL
