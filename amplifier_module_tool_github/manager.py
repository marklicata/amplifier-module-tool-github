"""
GitHub Manager

Manages the lifecycle of GitHub API interactions and provides access to GitHub tools.
"""

import logging
import os
import subprocess
import getpass
import re
from typing import Any
from datetime import datetime

try:
    from github import Github, Auth
    from github.GithubException import (
        BadCredentialsException,
        UnknownObjectException,
        RateLimitExceededException,
        GithubException,
    )
except ImportError:
    Github = None
    Auth = None
    BadCredentialsException = None
    UnknownObjectException = None
    RateLimitExceededException = None
    GithubException = None

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)

logger = logging.getLogger(__name__)


class GitHubManager:
    """Manages GitHub API interactions and tool access."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the GitHub manager.

        Args:
            config: Configuration dictionary with settings:
                - token: GitHub personal access token or GitHub App token (optional)
                - use_cli_auth: Use GitHub CLI authentication if token not provided (default: True)
                - prompt_if_missing: Prompt user for token if no auth found (default: True)
                - base_url: GitHub Enterprise URL (optional, defaults to github.com)
                - repositories: List of repository URLs or owner/repo strings to restrict access to (optional)
        """
        self.config = config
        self.token = config.get("token")
        self.use_cli_auth = config.get("use_cli_auth", True)
        self.prompt_if_missing = config.get("prompt_if_missing", True)
        self.base_url = config.get("base_url", "https://api.github.com")
        self.client = None
        
        # Parse and store configured repositories
        self.configured_repositories = self._parse_repositories(config.get("repositories", []))
        self.restrict_to_configured = len(self.configured_repositories) > 0

        if Github is None:
            raise ImportError(
                "PyGithub is not installed. Install it with: pip install PyGithub"
            )

    async def start(self):
        """Start the manager and initialize GitHub client."""
        logger.info("Starting GitHub manager")

        # Try to get authentication token from various sources
        if not self.token:
            self.token = self._get_token_from_sources()

        if not self.token:
            logger.warning("No GitHub authentication configured")
            if not self.prompt_if_missing:
                logger.warning(
                    "Authentication required but prompting is disabled. "
                    "Most operations will fail."
                )
                return
            
            # Prompt user for token
            self.token = self._prompt_for_token()
            if not self.token:
                logger.warning("No token provided. Most operations will fail.")
                return

        try:
            # Initialize GitHub client with authentication
            auth = Auth.Token(self.token)
            
            if self.base_url != "https://api.github.com":
                # GitHub Enterprise
                self.client = Github(base_url=self.base_url, auth=auth)
            else:
                # GitHub.com
                self.client = Github(auth=auth)

            # Verify authentication
            user = self.client.get_user()
            logger.info(f"Authenticated as: {user.login}")

        except BadCredentialsException:
            logger.error("GitHub authentication failed - invalid token")
            raise AuthenticationError("Invalid GitHub token")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            raise

    def _get_token_from_sources(self) -> str | None:
        """
        Try to get GitHub token from various sources.
        
        Returns:
            Token string if found, None otherwise
        """
        # 1. Check environment variable
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            logger.info("Using GitHub token from environment variable")
            return token
        
        # 2. Try GitHub CLI authentication
        if self.use_cli_auth:
            token = self._get_token_from_cli()
            if token:
                logger.info("Using GitHub token from GitHub CLI")
                return token
        
        return None
    
    def _get_token_from_cli(self) -> str | None:
        """
        Get authentication token from GitHub CLI.
        
        Returns:
            Token string if CLI is authenticated, None otherwise
        """
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                token = result.stdout.strip()
                if token:
                    return token
            else:
                logger.debug(f"GitHub CLI not authenticated: {result.stderr}")
        except FileNotFoundError:
            logger.debug("GitHub CLI (gh) not found in PATH")
        except subprocess.TimeoutExpired:
            logger.warning("GitHub CLI command timed out")
        except Exception as e:
            logger.debug(f"Failed to get token from GitHub CLI: {e}")
        
        return None
    
    def _prompt_for_token(self) -> str | None:
        """
        Prompt user to enter their GitHub token interactively.
        
        Returns:
            Token string if provided, None otherwise
        """
        print("\n" + "="*70)
        print("GitHub Authentication Required")
        print("="*70)
        print("\nNo GitHub authentication found. Please provide a personal access token.")
        print("\nYou can create a token at: https://github.com/settings/tokens")
        print("\nAlternatively, authenticate with GitHub CLI: gh auth login")
        print("\nRequired token permissions:")
        print("  - repo (for private repositories)")
        print("  - public_repo (for public repositories only)")
        print("\nNote: Your token will not be stored. Set GITHUB_TOKEN environment")
        print("      variable or use GitHub CLI for persistent authentication.")
        print("="*70)
        
        try:
            token = getpass.getpass("\nEnter your GitHub token (input hidden): ").strip()
            if token:
                return token
            else:
                print("No token provided.")
        except (KeyboardInterrupt, EOFError):
            print("\nAuthentication cancelled.")
        
        return None

    async def stop(self):
        """Stop the manager and clean up resources."""
        logger.info("Stopping GitHub manager")
        if self.client:
            self.client.close()

    def is_authenticated(self) -> bool:
        """Check if GitHub client is authenticated."""
        return self.client is not None
    
    def _parse_repositories(self, repositories: list[str]) -> set[str]:
        """
        Parse repository configurations from URLs or owner/repo format.
        
        Args:
            repositories: List of repository identifiers (URLs or owner/repo)
        
        Returns:
            Set of normalized repository names in owner/repo format
        """
        parsed = set()
        
        for repo in repositories:
            normalized = self._normalize_repository(repo)
            if normalized:
                parsed.add(normalized)
                logger.debug(f"Configured repository: {normalized}")
        
        if parsed:
            logger.info(f"Restricting access to {len(parsed)} configured repositories")
        
        return parsed
    
    def _normalize_repository(self, repo: str) -> str | None:
        """
        Normalize a repository identifier to owner/repo format.
        
        Accepts:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git
        - owner/repo
        
        Args:
            repo: Repository identifier
        
        Returns:
            Normalized repository name or None if invalid
        """
        repo = repo.strip()
        
        # Pattern 1: HTTPS URL (https://github.com/owner/repo or https://github.com/owner/repo.git)
        https_match = re.match(r'https?://[^/]+/([^/]+/[^/]+?)(?:\.git)?/?$', repo)
        if https_match:
            return https_match.group(1)
        
        # Pattern 2: SSH URL (git@github.com:owner/repo.git)
        ssh_match = re.match(r'git@[^:]+:([^/]+/[^/]+?)(?:\.git)?$', repo)
        if ssh_match:
            return ssh_match.group(1)
        
        # Pattern 3: Direct owner/repo format
        if re.match(r'^[^/]+/[^/]+$', repo):
            return repo
        
        logger.warning(f"Could not parse repository identifier: {repo}")
        return None
    
    def is_repository_allowed(self, repo_name: str) -> bool:
        """
        Check if a repository is allowed based on configuration.
        
        Args:
            repo_name: Repository name in owner/repo format
        
        Returns:
            True if repository is allowed, False otherwise
        """
        # If no repositories configured, allow all
        if not self.restrict_to_configured:
            return True
        
        # Normalize the repo name for comparison
        normalized = self._normalize_repository(repo_name)
        if not normalized:
            return False
        
        return normalized in self.configured_repositories
    
    def get_configured_repositories(self) -> list[str]:
        """
        Get the list of configured repositories.
        
        Returns:
            List of repository names in owner/repo format
        """
        return sorted(self.configured_repositories)

    def get_repository(self, repo_full_name: str):
        """
        Get a repository object.

        Args:
            repo_full_name: Full repository name (owner/repo)

        Returns:
            Repository object

        Raises:
            AuthenticationError: If not authenticated
            RepositoryNotFoundError: If repository not found
        """
        if not self.is_authenticated():
            raise AuthenticationError("GitHub client not authenticated")

        try:
            return self.client.get_repo(repo_full_name)
        except UnknownObjectException:
            raise RepositoryNotFoundError(repo_full_name)
        except RateLimitExceededException as e:
            reset_time = datetime.fromtimestamp(e.reset_timestamp).isoformat()
            raise RateLimitError(reset_time)

    def get_rate_limit(self) -> dict[str, Any]:
        """
        Get current rate limit information.

        Returns:
            Dictionary with rate limit details
        """
        if not self.is_authenticated():
            return {"authenticated": False}

        rate_limit = self.client.get_rate_limit()
        rate = rate_limit.rate

        return {
            "authenticated": True,
            "limit": rate.limit,
            "remaining": rate.remaining,
            "reset": rate.reset.isoformat(),
            "used": rate.limit - rate.remaining,
        }
