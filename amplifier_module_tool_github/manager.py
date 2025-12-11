"""
GitHub Manager

Manages the lifecycle of GitHub API interactions and provides access to GitHub tools.
"""

import logging
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
                - token: GitHub personal access token or GitHub App token (required)
                - base_url: GitHub Enterprise URL (optional, defaults to github.com)
        """
        self.config = config
        self.token = config.get("token")
        self.base_url = config.get("base_url", "https://api.github.com")
        self.client = None

        if Github is None:
            raise ImportError(
                "PyGithub is not installed. Install it with: pip install PyGithub"
            )

    async def start(self):
        """Start the manager and initialize GitHub client."""
        logger.info("Starting GitHub manager")

        if not self.token:
            logger.warning(
                "No GitHub token provided. Most operations will fail. "
                "Configure a personal access token or GitHub App token in the config."
            )
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

    async def stop(self):
        """Stop the manager and clean up resources."""
        logger.info("Stopping GitHub manager")
        if self.client:
            self.client.close()

    def is_authenticated(self) -> bool:
        """Check if GitHub client is authenticated."""
        return self.client is not None

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
        core = rate_limit.core

        return {
            "authenticated": True,
            "limit": core.limit,
            "remaining": core.remaining,
            "reset": core.reset.isoformat(),
            "used": core.limit - core.remaining,
        }
