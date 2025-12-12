"""
Example: Repository Access Control

Demonstrates how to restrict GitHub tool access to specific repositories.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the module without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import yaml
from amplifier_module_tool_github import GitHubUnifiedTool, GitHubManager


def load_config_from_amplifier_settings() -> dict:
    """Load GitHub config from .amplifier/settings.yaml if it exists."""
    settings_path = Path.home() / ".amplifier" / "settings.yaml"
    
    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
                return settings.get('modules', {}).get('github', {})
        except Exception as e:
            print(f"Warning: Could not load .amplifier/settings.yaml: {e}")
            return {}
    return {}


async def example_unrestricted_access():
    """Example: No repository restrictions (default)."""
    print("\n" + "="*70)
    print("Example 1: Unrestricted Access (Default)")
    print("="*70)
    
    config = {}  # No repositories configured
    manager = GitHubManager(config)
    await manager.start()
    
    print(f"Restrict to configured repos: {manager.restrict_to_configured}")
    print(f"Configured repositories: {manager.get_configured_repositories()}")
    
    # All repositories allowed
    print(f"\nCan access microsoft/vscode: {manager.is_repository_allowed('microsoft/vscode')}")
    print(f"Can access python/cpython: {manager.is_repository_allowed('python/cpython')}")
    print(f"Can access any/repo: {manager.is_repository_allowed('any/repo')}")
    
    await manager.stop()


async def example_restricted_access():
    """Example: Restricted to specific repositories."""
    print("\n" + "="*70)
    print("Example 2: Restricted Access")
    print("="*70)
    
    config = {
        "repositories": [
            "https://github.com/microsoft/vscode",
            "git@github.com:python/cpython.git",
            "facebook/react",  # Direct owner/repo format
        ]
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    print(f"Restrict to configured repos: {manager.restrict_to_configured}")
    print(f"Configured repositories: {manager.get_configured_repositories()}")
    
    # Check access
    print(f"\nCan access microsoft/vscode: {manager.is_repository_allowed('microsoft/vscode')}")
    print(f"Can access python/cpython: {manager.is_repository_allowed('python/cpython')}")
    print(f"Can access facebook/react: {manager.is_repository_allowed('facebook/react')}")
    print(f"Can access other/repo: {manager.is_repository_allowed('other/repo')}")  # False!
    
    await manager.stop()


async def example_url_format_flexibility():
    """Example: Various URL formats are normalized."""
    print("\n" + "="*70)
    print("Example 3: URL Format Flexibility")
    print("="*70)
    
    config = {
        "repositories": [
            "microsoft/vscode",  # Configure with direct format
        ]
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    print(f"Configured: {manager.get_configured_repositories()}")
    
    # All these formats resolve to the same repository
    print(f"\nAccess check with 'microsoft/vscode': {manager.is_repository_allowed('microsoft/vscode')}")
    print(f"Access check with HTTPS URL: {manager.is_repository_allowed('https://github.com/microsoft/vscode')}")
    print(f"Access check with SSH URL: {manager.is_repository_allowed('git@github.com:microsoft/vscode.git')}")
    
    await manager.stop()


async def example_tool_enforcement():
    """Example: Tool operations respect repository restrictions."""
    print("\n" + "="*70)
    print("Example 4: Tool-Level Enforcement")
    print("="*70)
    
    config = {
        "repositories": [
            "microsoft/vscode",  # Only this repo allowed
        ],
        "prompt_if_missing": False,
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    if not manager.is_authenticated():
        print("Not authenticated. Skipping tool execution examples.")
        await manager.stop()
        return
    
    tool = GitHubUnifiedTool(manager)
    
    # Try to access allowed repository
    print("\nAttempting to list issues in microsoft/vscode (allowed)...")
    result1 = await tool.execute({
        "operation": "list_issues",
        "parameters": {
            "repository": "microsoft/vscode",
            "limit": 1
        }
    })
    print(f"Result: {'Success' if result1.success else 'Failed'}")
    if result1.success:
        print(f"Found {len(result1.output.get('issues', []))} issues")
    
    # Try to access disallowed repository
    print("\nAttempting to list issues in python/cpython (NOT allowed)...")
    result2 = await tool.execute({
        "operation": "list_issues",
        "parameters": {
            "repository": "python/cpython",
            "limit": 1
        }
    })
    print(f"Result: {'Success' if result2.success else 'Failed'}")
    if not result2.success:
        print(f"Error: {result2.error.get('message', 'Unknown error')}")
    
    await manager.stop()


async def example_duplicate_handling():
    """Example: Duplicate repositories are automatically deduplicated."""
    print("\n" + "="*70)
    print("Example 5: Duplicate Handling")
    print("="*70)
    
    config = {
        "repositories": [
            "https://github.com/microsoft/vscode",
            "git@github.com:microsoft/vscode.git",
            "microsoft/vscode",
            "https://github.com/microsoft/vscode.git",
        ]
    }
    
    manager = GitHubManager(config)
    await manager.stop()
    
    print(f"Input: 4 repository identifiers (all pointing to microsoft/vscode)")
    print(f"Configured repositories: {manager.get_configured_repositories()}")
    print(f"Count: {len(manager.get_configured_repositories())} (duplicates removed)")
    
    await manager.stop()


async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Repository Access Control Examples")
    print("="*70)
    print("\nThese examples demonstrate how to restrict GitHub tool access")
    print("to specific repositories for security and scope control.")
    
    await example_unrestricted_access()
    await example_restricted_access()
    await example_url_format_flexibility()
    await example_tool_enforcement()
    await example_duplicate_handling()
    
    print("\n" + "="*70)
    print("Examples Complete")
    print("="*70)
    print("\nKey takeaways:")
    print("- By default, all repositories are accessible")
    print("- Configure 'repositories' list to restrict access")
    print("- Supports multiple URL formats (HTTPS, SSH, owner/repo)")
    print("- Tool operations automatically enforce restrictions")
    print("- Duplicates are automatically handled")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
