"""
Example usage of the unified GitHub tool.

This demonstrates how to use the single 'github' tool with different operations.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the module without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import yaml
from amplifier_module_tool_github import GitHubManager, GitHubUnifiedTool


def load_config_from_amplifier_settings() -> dict:
    """Load GitHub config from .amplifier/settings.yaml if it exists."""
    settings_path = Path.home() / ".amplifier" / "settings.yaml"
    
    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
                config = settings.get('modules', {}).get('github', {})
                print(f"✓ Loaded config from {settings_path}")
                return config
        except Exception as e:
            print(f"Warning: Could not load .amplifier/settings.yaml: {e}")
            return {}
    else:
        print(f"Note: No .amplifier/settings.yaml found at {settings_path}")
        return {}


async def example_list_issues():
    """Example: List issues in a repository."""
    print("\n" + "="*70)
    print("Example 1: List Issues")
    print("="*70)
    
    # Load config from .amplifier/settings.yaml (or use empty dict)
    config = load_config_from_amplifier_settings()
    
    # Initialize manager (will use auto-detected auth)
    manager = GitHubManager(config)
    await manager.start()
    
    if not manager.is_authenticated():
        print("Not authenticated. Please set up authentication first.")
        return
    
    # Create the unified tool
    tool = GitHubUnifiedTool(manager)
    
    # Execute operation
    result = await tool.execute({
        "operation": "list_issues",
        "parameters": {
            "repository": "microsoft/vscode",
            "state": "open",
            "labels": ["bug"],
            "limit": 5
        }
    })
    
    if result.success:
        issues = result.output.get("issues", [])
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  #{issue['number']}: {issue['title']}")
    else:
        print(f"Error: {result.error}")
    
    await manager.stop()


async def example_create_issue():
    """Example: Create a new issue."""
    print("\n" + "="*70)
    print("Example 2: Create Issue")
    print("="*70)
    
    config = load_config_from_amplifier_settings()
    manager = GitHubManager(config)
    await manager.start()
    
    if not manager.is_authenticated():
        print("Not authenticated. Please set up authentication first.")
        return
    
    tool = GitHubUnifiedTool(manager)
    
    # Note: Change to your own repository
    result = await tool.execute({
        "operation": "create_issue",
        "parameters": {
            "repository": "your-username/your-repo",  # Change this!
            "title": "Test issue from unified tool",
            "body": "This issue was created using the unified GitHub tool.",
            "labels": ["test"]
        }
    })
    
    if result.success:
        issue = result.output.get("issue", {})
        print(f"Created issue #{issue['number']}")
        print(f"URL: {issue['url']}")
    else:
        print(f"Error: {result.error}")
    
    await manager.stop()


async def example_get_file_content():
    """Example: Get file contents from a repository."""
    print("\n" + "="*70)
    print("Example 3: Get File Content")
    print("="*70)
    
    config = load_config_from_amplifier_settings()
    manager = GitHubManager(config)
    await manager.start()
    
    if not manager.is_authenticated():
        print("Not authenticated. Please set up authentication first.")
        return
    
    tool = GitHubUnifiedTool(manager)
    
    result = await tool.execute({
        "operation": "get_file_content",
        "parameters": {
            "repository": "microsoft/vscode",
            "path": "README.md"
        }
    })
    
    if result.success:
        content = result.output.get("content", "")
        print(f"File: {result.output.get('path')}")
        print(f"Size: {result.output.get('size')} bytes")
        print(f"First 200 characters:")
        print(content[:200] + "...")
    else:
        print(f"Error: {result.error}")
    
    await manager.stop()


async def example_list_pull_requests():
    """Example: List pull requests."""
    print("\n" + "="*70)
    print("Example 4: List Pull Requests")
    print("="*70)
    
    config = load_config_from_amplifier_settings()
    manager = GitHubManager(config)
    await manager.start()
    
    if not manager.is_authenticated():
        print("Not authenticated. Please set up authentication first.")
        return
    
    tool = GitHubUnifiedTool(manager)
    
    result = await tool.execute({
        "operation": "list_pull_requests",
        "parameters": {
            "repository": "microsoft/vscode",
            "state": "open",
            "limit": 5
        }
    })
    
    if result.success:
        prs = result.output.get("pull_requests", [])
        print(f"Found {len(prs)} pull requests:")
        for pr in prs:
            print(f"  #{pr['number']}: {pr['title']}")
    else:
        print(f"Error: {result.error}")
    
    await manager.stop()


async def example_list_operations():
    """Example: List all available operations."""
    print("\n" + "="*70)
    print("Example 5: List All Operations")
    print("="*70)
    
    manager = GitHubManager({"prompt_if_missing": False})
    await manager.start()
    
    tool = GitHubUnifiedTool(manager)
    
    operations = tool.list_operations()
    
    print(f"Total operations available: {len(operations)}\n")
    
    # Group by category
    categories = {}
    for op in operations:
        # Infer category from operation name
        if "issue" in op["operation"]:
            category = "Issues"
        elif "pull_request" in op["operation"]:
            category = "Pull Requests"
        elif "repository" in op["operation"] or "repo" in op["operation"] or "content" in op["operation"]:
            category = "Repositories"
        elif "commit" in op["operation"]:
            category = "Commits"
        elif "branch" in op["operation"]:
            category = "Branches"
        elif "release" in op["operation"] or "tag" in op["operation"]:
            category = "Releases"
        elif "workflow" in op["operation"]:
            category = "Workflows"
        else:
            category = "Other"
        
        if category not in categories:
            categories[category] = []
        categories[category].append(op)
    
    # Print by category
    for category in sorted(categories.keys()):
        print(f"{category} ({len(categories[category])} operations):")
        for op in categories[category]:
            print(f"  - {op['operation']}")
        print()
    
    await manager.stop()


async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("GitHub Unified Tool Examples")
    print("="*70)
    print("\nThis script demonstrates the unified 'github' tool interface.")
    print("All 34 GitHub operations are accessible through a single tool.\n")
    
    # Run examples
    await example_list_issues()
    # await example_create_issue()  # Uncomment and set your repo
    await example_get_file_content()
    await example_list_pull_requests()
    await example_list_operations()
    
    print("\n" + "="*70)
    print("Examples Complete")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
