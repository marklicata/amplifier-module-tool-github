# GitHub Module Examples

This directory contains examples demonstrating how to use the amplifier-module-tool-github.

## Running the Examples

The examples can be run directly without installing the package:

```powershell
# From the project root
python examples/auth_demo.py
python examples/repository_config_demo.py
python examples/unified_tool_demo.py
```

The examples automatically:
1. Add the parent directory to Python's path (no installation needed)
2. Load configuration from `~/.amplifier/settings.yaml` if it exists
3. Fall back to auto-detected authentication if no config file is found

## Configuration

The examples will look for configuration in `~/.amplifier/settings.yaml`. You can create this file to customize authentication and repository access.

### Example Configuration

Copy `settings.yaml.example` to `~/.amplifier/settings.yaml`:

```yaml
modules:
  github:
    # Authentication (auto-detected if not specified)
    use_cli_auth: true        # Use GitHub CLI (gh auth login)
    prompt_if_missing: true   # Prompt if no auth found
    
    # Repository restrictions (optional)
    repositories: []          # Empty = allow all repos
```

See [CONFIGURATION.md](../CONFIGURATION.md) for detailed configuration options.

## Available Examples

### 1. `auth_demo.py`
Demonstrates different authentication methods:
- Explicit token in config
- Environment variables (GITHUB_TOKEN, GH_TOKEN)
- GitHub CLI authentication (gh auth login)
- Interactive prompt
- Auto-detection (tries all methods in order)

### 2. `repository_config_demo.py`
Shows repository access control features:
- Unrestricted access (default)
- Restricted to specific repositories
- URL format flexibility
- Cross-repository queries

### 3. `unified_tool_demo.py`
Demonstrates the unified GitHub tool:
- List issues across repositories
- Create issues
- Get file contents
- List pull requests
- Browse all 34 available operations

## Authentication Setup

### Option 1: GitHub CLI (Recommended)
```bash
gh auth login
```

### Option 2: Environment Variable
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

### Option 3: Create Config File
```yaml
# ~/.amplifier/settings.yaml
modules:
  github:
    token: ghp_your_token_here
```

## Troubleshooting

### ModuleNotFoundError
If you see `ModuleNotFoundError: No module named 'amplifier_module_tool_github'`, the examples should now work without installation. The sys.path manipulation at the top of each example file handles this.

### ImportError with PyYAML
If you see `ImportError: No module named 'yaml'`, install PyYAML:
```bash
pip install pyyaml
```

### Authentication Errors
- Make sure you're authenticated with GitHub CLI: `gh auth status`
- Or set GITHUB_TOKEN environment variable
- Or create `~/.amplifier/settings.yaml` with your token

## Next Steps

- Read [CONFIGURATION.md](../CONFIGURATION.md) for advanced configuration
- See [DEVELOPMENT.md](../DEVELOPMENT.md) for contributing
- Check [QUICKSTART.md](../QUICKSTART.md) for integration with Amplifier
