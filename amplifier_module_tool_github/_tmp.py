import subprocess
from github import Github, Auth
from github.GithubException import (
    BadCredentialsException,
    UnknownObjectException,
    RateLimitExceededException,
    GithubException,
)

async def main():
        """Start the manager and initialize GitHub client."""
        print("Starting GitHub manager")

        token = None
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(result)
            if result.returncode == 0:
                token = result.stdout.strip()
        except FileNotFoundError:
            print("GitHub CLI (gh) not found in PATH")
        except subprocess.TimeoutExpired:
            print("GitHub CLI command timed out")
        except Exception as e:
            print(f"Failed to get token from GitHub CLI: {e}")


        try:
            # Initialize GitHub client with authentication
            auth = Auth.Token(token)
            
            github_client = Github(auth=auth, base_url="https://api.github.com")

            # Verify authentication
            github_user = github_client.get_user()
            print(f"Authenticated as: {github_user.login}")
        except Exception as e:
            print(f"Failed to initialize GitHub client: {e}")
            raise



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())