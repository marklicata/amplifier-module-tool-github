# Configuration Guide

This guide explains how to configure the GitHub module in your `.amplifier/settings.yaml` file.

## Quick Start

Create or edit `.amplifier/settings.yaml` in your project root:

```yaml
# .amplifier/settings.yaml

modules:
  github:
    # Authentication (optional - will auto-detect if not provided)
    use_cli_auth: true        # Use GitHub CLI authentication (default: true)
    prompt_if_missing: true   # Prompt for token if no auth found (default: true)
    
    # Repository access control (optional)
    repositories: []  # Empty = allow all repositories
```

See [`examples/settings.yaml.example`](examples/settings.yaml.example) for a complete template.

## Repository Access Control

### Restrict to Specific Repositories

```yaml
# .amplifier/settings.yaml

modules:
  github:
    repositories:
      - https://github.com/microsoft/vscode
      - git@github.com:python/cpython.git
      - facebook/react  # Direct owner/repo format also works
```

**Cross-Repository Queries:** When repositories are configured, operations like `list_issues` and `list_pull_requests` can query across ALL configured repos when you don't provide a `repository` parameter!

Example:
```python
# Query ALL configured repos for issues assigned to you
result = await amplifier.execute_tool("github", {
    "operation": "list_issues",
    "parameters": {
        # No "repository" parameter = queries all configured repos!
        "assignee": "myusername",
        "state": "open"
    }
})
```

### Supported URL Formats

All of these formats work:

```yaml
modules:
  github:
    repositories:
      # HTTPS URLs
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      
      # SSH URLs
      - git@github.com:owner/repo.git
      - git@github.com:owner/repo
      
      # Direct format
      - owner/repo
      
      # GitHub Enterprise URLs (when base_url is configured)
      - https://github.company.com/owner/repo
```

## Authentication Options

### Option 1: GitHub CLI (Recommended)

```bash
# One-time setup
gh auth login
```

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true  # Will use gh CLI token automatically
```

### Option 2: Environment Variable

```bash
# Set in your shell
export GITHUB_TOKEN="ghp_your_token_here"
# or
export GH_TOKEN="ghp_your_token_here"
```

```yaml
# .amplifier/settings.yaml
modules:
  github:
    # No token needed - will read from environment
```

### Option 3: Direct Token

```yaml
# .amplifier/settings.yaml
modules:
  github:
    token: ghp_your_personal_access_token_here
```

**⚠️ Warning:** Don't commit tokens to version control! Use environment variables or CLI auth instead.

### Option 4: Interactive Prompt

```yaml
# .amplifier/settings.yaml
modules:
  github:
    prompt_if_missing: true  # Will prompt on startup if no auth found
```

## Configuration Examples

### Example 1: Unrestricted Access with CLI Auth

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true
    prompt_if_missing: true
    # No repositories list = access all repos
```

### Example 2: Restricted to Work Repositories

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true
    repositories:
      - your-company/frontend-app
      - your-company/backend-api
      - your-company/shared-lib
```

### Example 3: GitHub Enterprise

```yaml
# .amplifier/settings.yaml
modules:
  github:
    token: ghp_enterprise_token_here
    base_url: https://github.company.com/api/v3
    repositories:
      - https://github.company.com/internal/project1
      - https://github.company.com/internal/project2
```

### Example 4: Development with Multiple Orgs

```yaml
# .amplifier/settings.yaml
modules:
  github:
    use_cli_auth: true
    repositories:
      # Personal projects
      - yourusername/personal-project
      
      # Work projects
      - company/work-repo1
      - company/work-repo2
      
      # Open source contributions
      - microsoft/vscode
      - python/cpython
```

## Security Best Practices

1. **Never commit tokens** to `.amplifier/settings.yaml` if it's in version control
2. **Use GitHub CLI auth** for development (stores tokens securely)
3. **Use environment variables** for CI/CD and production
4. **Restrict repositories** to only what you need
5. **Use fine-grained tokens** with minimal required permissions

## Team Setup

For team projects, create an example file and add the actual config to `.gitignore`:

**Step 1:** Create `examples/settings.yaml.example` (committed to git)

```yaml
modules:
  github:
    # Team members configure their own auth
    use_cli_auth: true
    prompt_if_missing: true
    
    # Team repositories
    repositories:
      - your-company/repo1
      - your-company/repo2
```

**Step 2:** Add to `.gitignore`:

```
.amplifier/settings.yaml
```

**Step 3:** Team members copy and configure:

```bash
# Copy example
cp examples/settings.yaml.example .amplifier/settings.yaml

# Configure authentication (choose one):
# - Run: gh auth login
# - Set: export GITHUB_TOKEN="your_token"
# - Edit .amplifier/settings.yaml with token
```

## Token Permissions

Your GitHub token needs appropriate permissions:

- **Public repositories:** `public_repo` scope
- **Private repositories:** `repo` scope
- **Read-only access:** Ensure token has read permissions
- **Write access:** Token needs write permissions for create/update/delete operations

### Creating a Personal Access Token

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Amplifier GitHub Module"
4. Select required scopes:
   - `repo` (for private repos) or `public_repo` (for public repos only)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. Store securely using one of the authentication options above

## Troubleshooting

### "No authentication configured"

**Solutions:**
- Run `gh auth login` and ensure CLI auth is enabled
- Set `GITHUB_TOKEN` or `GH_TOKEN` environment variable
- Add `token` to your settings.yaml
- Enable `prompt_if_missing: true` to be prompted for token

### "Repository access denied"

**Solutions:**
- Check if repository is in your `repositories` list
- Ensure token has appropriate permissions
- Verify repository name format is `owner/repo`

### "Rate limit exceeded"

**Solutions:**
- Authenticate (unauthenticated requests have lower rate limits)
- Wait for rate limit to reset
- Use GitHub Enterprise with higher limits
- Implement caching in your application

## Advanced Configuration

### Custom GitHub Enterprise Base URL

```yaml
modules:
  github:
    base_url: https://github.company.com/api/v3
    token: ghp_enterprise_token
```

### Disable CLI Authentication

```yaml
modules:
  github:
    use_cli_auth: false  # Don't try CLI auth
    token: ghp_your_token
```

### Disable Interactive Prompts

```yaml
modules:
  github:
    prompt_if_missing: false  # Fail if no auth found, don't prompt
```

### Allow All Repositories

```yaml
modules:
  github:
    # Don't include 'repositories' key, or set to empty list
    repositories: []
```
