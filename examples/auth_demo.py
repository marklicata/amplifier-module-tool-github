"""
Authentication Demo for GitHub Module

This script demonstrates the different authentication methods
supported by the amplifier-module-tool-github.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the module without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import yaml
from amplifier_module_tool_github import GitHubManager


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


async def demo_explicit_token():
    """Demo: Explicit token in config."""
    print("\n" + "="*70)
    print("Demo 1: Explicit Token Authentication")
    print("="*70)
    
    config = {
        "token": "ghp_your_token_here",  # Replace with real token
        "prompt_if_missing": False,  # Don't prompt if invalid
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    if manager.is_authenticated():
        print("✓ Successfully authenticated with explicit token")
        rate_limit = manager.get_rate_limit()
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
    else:
        print("✗ Authentication failed")
    
    await manager.stop()


async def demo_environment_variable():
    """Demo: Token from environment variable."""
    print("\n" + "="*70)
    print("Demo 2: Environment Variable Authentication")
    print("="*70)
    print("Set GITHUB_TOKEN or GH_TOKEN environment variable")
    
    config = {
        "prompt_if_missing": False,  # Don't prompt, just use environment
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    if manager.is_authenticated():
        print("✓ Successfully authenticated from environment variable")
        rate_limit = manager.get_rate_limit()
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
    else:
        print("✗ No token found in environment")
    
    await manager.stop()


async def demo_cli_auth():
    """Demo: GitHub CLI authentication."""
    print("\n" + "="*70)
    print("Demo 3: GitHub CLI Authentication")
    print("="*70)
    print("Requires: gh auth login")
    
    config = {
        "use_cli_auth": True,
        "prompt_if_missing": False,
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    if manager.is_authenticated():
        print("✓ Successfully authenticated with GitHub CLI")
        rate_limit = manager.get_rate_limit()
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
    else:
        print("✗ GitHub CLI not authenticated (run: gh auth login)")
    
    await manager.stop()


async def demo_interactive_prompt():
    """Demo: Interactive prompt for token."""
    print("\n" + "="*70)
    print("Demo 4: Interactive Prompt")
    print("="*70)
    print("Will prompt for token if no other auth method is available")
    
    config = {
        "use_cli_auth": False,  # Disable CLI auth to force prompt
        "prompt_if_missing": True,  # Enable prompt
    }
    
    manager = GitHubManager(config)
    await manager.start()
    
    if manager.is_authenticated():
        print("✓ Successfully authenticated")
        rate_limit = manager.get_rate_limit()
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
    else:
        print("✗ No authentication provided")
    
    await manager.stop()


async def demo_auto_detection():
    """Demo: Automatic authentication detection."""
    print("\n" + "="*70)
    print("Demo 5: Automatic Authentication Detection")
    print("="*70)
    print("Tries in order: explicit token → env var → CLI → prompt")
    
    config = {}  # Empty config - will try all methods
    
    manager = GitHubManager(config)
    await manager.start()
    
    if manager.is_authenticated():
        print("✓ Successfully authenticated (auto-detected)")
        rate_limit = manager.get_rate_limit()
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
        
        # Show which method was used
        if manager.token:
            print(f"  Token starts with: {manager.token[:7]}...")
    else:
        print("✗ No authentication found")
    
    await manager.stop()


async def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("GitHub Module Authentication Demos")
    print("="*70)
    print("\nThis script demonstrates the various authentication methods")
    print("supported by amplifier-module-tool-github.")
    
    # Comment out demos you don't want to run
    
    # await demo_explicit_token()
    # await demo_environment_variable()
    await demo_cli_auth()
    # await demo_interactive_prompt()  # Uncomment to test prompting
    await demo_auto_detection()
    
    print("\n" + "="*70)
    print("Demos Complete")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
