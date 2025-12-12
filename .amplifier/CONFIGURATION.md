# Amplifier Configuration for GitHub Module

This file shows how to configure the GitHub module in your `.amplifier/settings.yaml` file.

## Basic Configuration

```yaml
# .amplifier/settings.yaml

modules:
  github:
    # Authentication (optional - will auto-detect if not provided)
    token: ghp_your_personal_access_token_here
    
    # Or use environment variables/CLI auth (recommended)
    use_cli_auth: true        # Use GitHub CLI authentication (default: true)
    prompt_if_missing: true   # Prompt for token if no auth found (default: true)
    
    # GitHub Enterprise (optional)
    base_url: https://api.github.com
    
    # Repository access control (optional)
    repositories: []  # Empty = allow all repositories
```

## Repository Access Control

### Restrict to Specific Repositories

```yaml
# .amplifier/settings.yaml

modules:
  github:
    # Limit access to only these repositories
    repositories:
      - https://github.com/microsoft/vscode
      - git@github.com:python/cpython.git
      - facebook/react  # Direct owner/repo format also works
```

### Mixed Formats Supported

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

## Complete Examples

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

## Setting Up for Team

For team projects, create a `.amplifier/settings.yaml.example`:

```yaml
# .amplifier/settings.yaml.example
modules:
  github:
    # Authentication - team members should configure their own:
    # Option 1: Run 'gh auth login' (recommended)
    # Option 2: Set GITHUB_TOKEN environment variable
    # Option 3: Set token below (DO NOT COMMIT)
    use_cli_auth: true
    prompt_if_missing: true
    
    # Repositories - team has access to these
    repositories:
      - your-company/repo1
      - your-company/repo2
      - your-company/repo3
```

Then in `.gitignore`:

```
.amplifier/settings.yaml
```

Team members copy the example and configure their authentication.
