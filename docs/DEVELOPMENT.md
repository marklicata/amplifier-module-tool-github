# Development Guide

Guide for developers working on the GitHub module.

## Setup Development Environment

### 1. Clone and Setup

```bash
cd amplifier-module-tool-github

# Install with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### 2. Configure GitHub Token

For testing, set up a personal access token:

```bash
# Linux/Mac
export GITHUB_TOKEN="ghp_your_token_here"

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_your_token_here"
```

## Running Tests

The project has comprehensive test coverage with **225 tests** achieving a **100% pass rate**.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=amplifier_module_tool_github

# Run specific test file
pytest tests/test_tools.py

# Run comprehensive tests only
pytest tests/test_*_comprehensive.py -v

# Run with verbose output
pytest -v

# Quick test status check
pytest tests/ --tb=no -q
```

### Test Organization
- **Original tests** (60): Basic functionality and tool properties
- **Comprehensive tests** (165): Extensive coverage across all tools
  - Issues: 30 tests
  - Pull Requests: 27 tests
  - Repositories: 19 tests
  - Branches/Commits: 34 tests
  - Releases/Actions: 25 tests
  - Edge Cases: 40 tests

## Code Style

### Python Version
- Minimum: Python 3.11
- Use modern Python features (type hints, match statements, etc.)

### Type Hints
All code must include type hints:

```python
def process_issue(issue: Issue) -> dict[str, Any]:
    """Process issue data."""
    return {"number": issue.number}
```

### Docstrings
Use Google-style docstrings:

```python
def create_tool(name: str) -> Tool:
    """
    Create a new tool instance.

    Args:
        name: The tool name

    Returns:
        Tool instance

    Raises:
        ValueError: If name is invalid
    """
    pass
```

## Adding a New Tool

### Step 1: Create Tool File

Create your tool in the appropriate category subdirectory.

For example, for a new issue tool: `amplifier_module_tool_github/tools/issues/your_tool.py`

```python
"""Description of your tool."""

from typing import Any
from ..base import GitHubBaseTool, ToolResult
from ...exceptions import GitHubError


class YourTool(GitHubBaseTool):
    """Tool to do something."""

    @property
    def name(self) -> str:
        return "github_your_tool"

    @property
    def description(self) -> str:
        return "Description of what the tool does."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "Repository name"
                },
                # Add more properties
            },
            "required": ["repository"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute the tool."""
        # Check authentication
        auth_error = self._check_authentication()
        if auth_error:
            return auth_error

        # Get parameters
        repository = input_data.get("repository")

        try:
            # Implement tool logic
            repo = self.manager.get_repository(repository)
            # ... do work ...

            return ToolResult(
                success=True,
                output={
                    "repository": repository,
                    # ... your output ...
                }
            )

        except GitHubError as e:
            return ToolResult(success=False, error=e.to_dict())

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Unexpected error: {str(e)}",
                    "code": "UNEXPECTED_ERROR"
                }
            )
```

### Step 2: Export Tool

First, update the category's `__init__.py` (e.g., `amplifier_module_tool_github/tools/issues/__init__.py`):

```python
from .your_tool import YourTool

__all__ = [
    # ... existing tools ...
    "YourTool",
]
```

Then, update the main tools `__init__.py` (`amplifier_module_tool_github/tools/__init__.py`):

```python
from .issues import (
    # ... existing tools ...
    YourTool,
)

__all__ = [
    # ... existing tools ...
    "YourTool",
]
```

### Step 3: Register Tool

Update `amplifier_module_tool_github/__init__.py`:

```python
from .tools import (
    # ... existing tools ...
    YourTool,
)

async def mount(coordinator, config):
    # ...
    tools = [
        # ... existing tools ...
        YourTool(manager),
    ]
    # ...
```

### Step 4: Add Tests

Create tests in `tests/test_tools.py`:

```python
class TestYourTool:
    """Tests for YourTool."""

    def test_tool_properties(self):
        """Test tool name and schema."""
        manager = Mock()
        tool = YourTool(manager)
        
        assert tool.name == "github_your_tool"
        assert "something" in tool.description.lower()
        assert tool.input_schema["type"] == "object"

    @pytest.mark.asyncio
    async def test_execute_without_auth(self):
        """Test execution without authentication."""
        manager = Mock()
        manager.is_authenticated.return_value = False
        tool = YourTool(manager)
        
        result = await tool.execute({"repository": "test/repo"})
        assert not result.success
```

### Step 5: Update Documentation

Update `README.md` with tool documentation:

```markdown
### `github_your_tool`
Description of what the tool does.

**Parameters:**
- `repository` (string, required): Description

**Example:**
\`\`\`json
{
  "repository": "owner/repo"
}
\`\`\`
```

## Error Handling

### Using Custom Exceptions

Always use custom exceptions from `exceptions.py`:

```python
from ..exceptions import (
    RepositoryNotFoundError,
    ValidationError,
)

# Raise custom exception
if not valid:
    raise ValidationError("Invalid input")

# Catch and convert to ToolResult
try:
    # ... operation ...
except RepositoryNotFoundError as e:
    return ToolResult(success=False, error=e.to_dict())
```

### Adding New Exceptions

If you need a new exception type, add it to `exceptions.py`:

```python
class NewError(GitHubError):
    """Raised when something specific happens."""

    def __init__(self, details: str):
        super().__init__(
            f"Description: {details}",
            code="NEW_ERROR"
        )
```

## Working with PyGithub

### Common Patterns

```python
# Get repository
repo = self.manager.get_repository("owner/repo")

# List issues
issues = repo.get_issues(state="open")
for issue in issues:
    print(issue.title)

# Get specific issue
issue = repo.get_issue(number=123)

# Create issue
issue = repo.create_issue(
    title="Title",
    body="Description",
    labels=["bug"]
)

# Update issue
issue.edit(state="closed")

# Add comment
comment = issue.create_comment("Comment text")
```

### Handling Pagination

PyGithub uses lazy loading for paginated results:

```python
# Get issues (returns PaginatedList)
issues = repo.get_issues(state="open")

# Iterate with limit
count = 0
for issue in issues:
    if count >= limit:
        break
    # Process issue
    count += 1
```

### Error Handling

```python
from github.GithubException import (
    UnknownObjectException,
    RateLimitExceededException,
    GithubException,
)

try:
    repo = self.manager.get_repository(name)
except UnknownObjectException:
    # Repository not found
    pass
except RateLimitExceededException as e:
    # Rate limited - e.reset_timestamp available
    pass
except GithubException as e:
    # Other GitHub API error
    # e.status, e.data available
    pass
```

## Manager Access

The manager provides helper methods:

```python
# Check authentication
if not self.manager.is_authenticated():
    # Handle unauthenticated case
    pass

# Get repository (with error handling)
repo = self.manager.get_repository("owner/repo")
# Raises RepositoryNotFoundError if not found
# Raises RateLimitError if rate limited

# Get rate limit info
rate_info = self.manager.get_rate_limit()
print(f"Remaining: {rate_info['remaining']}")
```

## Testing Guidelines

### Unit Tests

Mock external dependencies:

```python
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_tool_execution():
    # Mock manager
    manager = Mock()
    manager.is_authenticated.return_value = True
    
    # Mock repository
    mock_repo = Mock()
    manager.get_repository.return_value = mock_repo
    
    # Test tool
    tool = YourTool(manager)
    result = await tool.execute({"repository": "test/repo"})
    
    assert result.success
```

### Integration Tests

For integration tests with real GitHub API:

```python
import os
import pytest

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not set"
)
@pytest.mark.asyncio
async def test_real_github_api():
    """Test with real GitHub API."""
    config = {"token": os.getenv("GITHUB_TOKEN")}
    manager = GitHubManager(config)
    await manager.start()
    
    # Test real operations
    # ...
    
    await manager.stop()
```

Run integration tests:

```bash
# Run only integration tests
pytest -m integration

# Skip integration tests
pytest -m "not integration"
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if exists)
3. Run full test suite
4. Commit changes
5. Tag release: `git tag v0.2.0`
6. Push: `git push --tags`

## Useful Commands

```bash
# Format code (if using black)
black amplifier_module_tool_github tests

# Lint code (if using ruff)
ruff check amplifier_module_tool_github tests

# Type check (if using mypy)
mypy amplifier_module_tool_github

# Build package
python -m build

# Install locally
pip install -e .
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("amplifier_module_tool_github")
```

### Inspect GitHub Responses

```python
# In your tool
print(f"Issue data: {issue.raw_data}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure tests pass
5. Update documentation
6. Submit pull request

## Questions?

- Check existing issues
- Review documentation
- Ask in discussions
