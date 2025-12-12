# Quick Start Guide

Get started with the GitHub module for Amplifier in minutes!

## Prerequisites

- Python 3.11 or higher
- GitHub account
- One of the following for authentication:
  - GitHub personal access token (see Step 2)
  - GitHub CLI (`gh`) installed and authenticated
  - Interactive prompt (will ask for token on startup)

## Step 1: Installation

Install the module using pip or uv:

```bash
# Using pip
pip install amplifier-module-tool-github

# Using uv
uv pip install amplifier-module-tool-github
```

## Step 2: Authentication Setup

The module supports **three authentication methods** (tried in order):

### Option A: GitHub CLI (Recommended for Development)

Easiest option - uses your existing GitHub CLI credentials:

```bash
# Authenticate once with GitHub CLI
gh auth login
```

```python
from amplifier_module_tool_github import mount

# No token needed - will use gh CLI automatically
config = {}

await amplifier.mount_module(mount, config)
```

### Option B: Environment Variable

Set your token as an environment variable:

```bash
# Windows (PowerShell)
$env:GITHUB_TOKEN = "ghp_your_token_here"

# Linux/macOS
export GITHUB_TOKEN="ghp_your_token_here"
```

```python
from amplifier_module_tool_github import mount

# No token in config - will read from environment
config = {}

await amplifier.mount_module(mount, config)
```

### Option C: Direct Token Configuration

Provide token directly in config (good for production):

```python
from amplifier_module_tool_github import mount

config = {
    "token": "ghp_your_token_here",  # Your personal access token
}

await amplifier.mount_module(mount, config)
```

### Option D: Interactive Prompt

If no authentication is found, the module will prompt you:

```python
from amplifier_module_tool_github import mount

# Empty config - will prompt for token on startup
config = {}

await amplifier.mount_module(mount, config)
# Will display: "GitHub Authentication Required" prompt
```

To disable the prompt:

```python
config = {
    "prompt_if_missing": False  # No prompt, fail if no auth found
}
```

### Getting a Personal Access Token

If you need to create a token:

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Amplifier GitHub Module"
4. Select scopes:
   - `repo` (for private repos) or `public_repo` (for public repos only)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

## Step 3: Configure the Module

Configuration is done in `.amplifier/settings.yaml`. Create or edit this file:

### Basic Configuration

```yaml
# .amplifier/settings.yaml
modules:
  github:
    # Minimal config - uses auto-detection
    use_cli_auth: true        # Enable GitHub CLI auth (default: true)
    prompt_if_missing: true   # Prompt if no auth found (default: true)
```

### Advanced Configuration

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true
    prompt_if_missing: true
    base_url: https://api.github.com  # For GitHub Enterprise, change this
    
    # Optional: restrict to specific repos
    repositories:
      - https://github.com/microsoft/vscode
      - python/cpython
```

### Restricting to Specific Repositories

For security or to limit scope, you can configure specific repositories in `.amplifier/settings.yaml`:

```yaml
# .amplifier/settings.yaml
modules:
  github:
    repositories:
      - https://github.com/your-org/repo1
      - git@github.com:your-org/repo2.git
      - your-org/repo3  # owner/repo format
```

When configured, the tool will only allow operations on these repositories. Attempts to access other repos will return a permission error.

See [`.amplifier/CONFIGURATION.md`](.amplifier/CONFIGURATION.md) for complete configuration examples.

## Step 4: Use the GitHub Tool

The module provides a **single unified tool** called `github` with 34 operations.

All operations follow this pattern:

```python
result = await amplifier.execute_tool(
    "github",  # Single tool name
    {
        "operation": "operation_name",  # What to do
        "parameters": {                  # Operation-specific params
            # ... parameters
        }
    }
)
```

### Example 1: List Open Issues

```python
# List open bugs in a repository
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "list_issues",
        "parameters": {
            "repository": "microsoft/vscode",
            "state": "open",
            "labels": ["bug"],
            "limit": 10
        }
    }
)

if result.success:
    for issue in result.output["issues"]:
        print(f"#{issue['number']}: {issue['title']}")
```

### Example 2: Get Issue Details

```python
# Get details of a specific issue
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "get_issue",
        "parameters": {
            "repository": "microsoft/vscode",
            "issue_number": 12345,
            "include_comments": True
        }
    }
)

if result.success:
    issue = result.output["issue"]
    print(f"Title: {issue['title']}")
    print(f"Author: {issue['author']['login']}")
    print(f"State: {issue['state']}")
    if "comments" in issue:
        print(f"Comments: {len(issue['comments'])}")
```

### Example 3: Create a Pull Request

```python
# Create a new pull request
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "create_pull_request",
        "parameters": {
            "repository": "your-username/your-repo",
            "title": "Add dark mode feature",
            "body": "This PR implements dark mode...",
            "head": "feature/dark-mode",
            "base": "main"
        }
    }
)

if result.success:
    pr = result.output["pull_request"]
    print(f"Created PR #{pr['number']}: {pr['url']}")
```

### Example 4: Get File Contents

```python
# Read a file from a repository
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "get_file_content",
        "parameters": {
            "repository": "microsoft/vscode",
            "path": "README.md",
            "ref": "main"  # Optional: branch, tag, or commit
        }
    }
)

if result.success:
    content = result.output["content"]
    print(f"File size: {result.output['size']} bytes")
    print(f"Content: {content[:100]}...")  # First 100 chars
```

### Example 5: Trigger a Workflow

```python
# Trigger a GitHub Actions workflow
result = await amplifier.execute_tool(
    "github",
    {
        "operation": "trigger_workflow",
        "parameters": {
            "repository": "your-username/your-repo",
            "workflow_id": "ci.yml",
            "ref": "main",
            "inputs": {
                "environment": "production"
            }
        }
    }
)

if result.success:
    print("Workflow triggered successfully!")
```

## All Available Operations

The `github` tool supports 34 operations across these categories:

- **Issues**: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `comment_issue`
- **Pull Requests**: `list_pull_requests`, `get_pull_request`, `create_pull_request`, `update_pull_request`, `merge_pull_request`, `review_pull_request`
- **Repositories**: `get_repository`, `list_repositories`, `create_repository`, `get_file_content`, `list_repository_contents`
- **Commits**: `list_commits`, `get_commit`
- **Branches**: `list_branches`, `get_branch`, `create_branch`, `compare_branches`
- **Releases**: `list_releases`, `get_release`, `create_release`, `list_tags`, `create_tag`
- **Workflows**: `list_workflows`, `get_workflow`, `trigger_workflow`, `list_workflow_runs`, `get_workflow_run`, `cancel_workflow_run`, `rerun_workflow`

See the [README](README.md) for detailed documentation on each operation

```python
# Close an issue with updated labels
result = await amplifier.execute_tool(
    "github_update_issue",
    {
        "repository": "your-username/your-repo",
        "issue_number": 42,
        "state": "closed",
        "labels": ["bug", "fixed"]
    }
)

if result.success:
    print(f"Issue updated: {result.output['message']}")
```

### Example 5: Comment on an Issue

```python
# Add a comment to an issue
result = await amplifier.execute_tool(
    "github_comment_issue",
    {
        "repository": "your-username/your-repo",
        "issue_number": 42,
        "body": "This has been fixed in version 2.0. Please verify!"
    }
)

if result.success:
    print(f"Comment added: {result.output['comment']['url']}")
```

## Error Handling

Always check if the operation was successful:

```python
result = await amplifier.execute_tool("github_get_issue", {...})

if result.success:
    # Operation succeeded
    print(result.output)
else:
    # Operation failed
    error = result.error
    print(f"Error ({error['code']}): {error['message']}")
    
    # Common error codes:
    # - AUTHENTICATION_ERROR: Invalid or missing token
    # - REPOSITORY_NOT_FOUND: Repository doesn't exist
    # - ISSUE_NOT_FOUND: Issue doesn't exist
    # - RATE_LIMIT_EXCEEDED: Hit GitHub's rate limit
    # - PERMISSION_DENIED: Need more permissions
```

## Best Practices

### 1. Store Tokens Securely

Never hardcode tokens in your code:

```python
import os

config = {
    "token": os.getenv("GITHUB_TOKEN")  # From environment variable
}
```

### 2. Handle Rate Limits

GitHub has rate limits (5,000 requests/hour for authenticated users):

```python
if not result.success and result.error["code"] == "RATE_LIMIT_EXCEEDED":
    reset_time = result.error["message"]
    print(f"Rate limited until {reset_time}")
    # Wait or retry later
```

### 3. Use Specific Labels

When filtering issues, use specific labels:

```python
# Good: Specific labels
result = await amplifier.execute_tool(
    "github_list_issues",
    {
        "repository": "owner/repo",
        "labels": ["bug", "priority:high"]
    }
)
```

### 4. Limit Results

Don't fetch more data than needed:

```python
result = await amplifier.execute_tool(
    "github_list_issues",
    {
        "repository": "owner/repo",
        "limit": 20  # Only get 20 issues
    }
)
```

## What's Next?

- Check the [README.md](README.md) for full tool documentation
- See [TODO.md](TODO.md) for upcoming features
- Report issues on [GitHub Issues](https://github.com/microsoft/amplifier-module-tool-github/issues)

## Common Use Cases

### Use Case 1: Bug Triage Bot

```python
# List all open bugs that need triage
result = await amplifier.execute_tool(
    "github_list_issues",
    {
        "repository": "owner/repo",
        "state": "open",
        "labels": ["bug"],
        "assignee": "none"  # Unassigned
    }
)

# Analyze and assign bugs automatically
```

### Use Case 2: Issue Report Generator

```python
# Get all closed issues from last month
result = await amplifier.execute_tool(
    "github_list_issues",
    {
        "repository": "owner/repo",
        "state": "closed",
        "sort": "updated",
        "direction": "desc",
        "limit": 100
    }
)

# Generate report from issues
```

### Use Case 3: Automated Issue Updates

```python
# Find stale issues and add comment
stale_issues = await amplifier.execute_tool(
    "github_list_issues",
    {
        "repository": "owner/repo",
        "state": "open",
        "sort": "updated",
        "direction": "asc",
        "limit": 10
    }
)

for issue in stale_issues.output["issues"]:
    # Add comment to stale issue
    await amplifier.execute_tool(
        "github_comment_issue",
        {
            "repository": "owner/repo",
            "issue_number": issue["number"],
            "body": "This issue hasn't been updated in a while. Is it still relevant?"
        }
    )
```

## Troubleshooting

### Token Issues

```
Error: AUTHENTICATION_ERROR
```

- Check token is valid and not expired
- Verify token has correct permissions
- Ensure token is properly set in config

### Repository Access

```
Error: REPOSITORY_NOT_FOUND
```

- Check repository name format: `owner/repo`
- Verify you have access to the repository
- For private repos, ensure token has `repo` scope

### Rate Limiting

```
Error: RATE_LIMIT_EXCEEDED
```

- Wait until the reset time (included in error message)
- Reduce frequency of API calls
- Use filtering to reduce number of requests

## Need Help?

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/microsoft/amplifier-module-tool-github/issues)
- 💬 [Discussions](https://github.com/microsoft/amplifier/discussions)
