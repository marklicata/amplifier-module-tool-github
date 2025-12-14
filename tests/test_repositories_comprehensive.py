"""Comprehensive tests for GitHub Repository tools covering all scenarios."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tests.conftest import create_mock_datetime
from github.GithubException import GithubException, UnknownObjectException

from amplifier_module_tool_github.tools.repositories import (
    GetRepositoryTool,
    ListRepositoriesTool,
    CreateRepositoryTool,
    GetFileContentTool,
    ListRepositoryContentsTool,
)


class TestGetRepositoryToolComprehensive:
    """Comprehensive tests for GetRepositoryTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetRepositoryTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_repository_success(self, test_username):
        """Test successfully getting repository details."""
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = f"{test_username}/test-repo"
        mock_repo.description = "A test repository"
        mock_repo.html_url = "https://github.com/{test_username}/test-repo"
        mock_repo.private = False
        mock_repo.fork = False
        mock_repo.archived = False
        mock_repo.disabled = False
        mock_repo.default_branch = "main"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 42
        mock_repo.fork = False
        mock_repo.archived = False
        mock_repo.language = "Python"
        mock_repo.default_branch = "main"
        mock_repo.id = 12345
        mock_repo.forks_count = 10
        mock_repo.open_issues_count = 5
        mock_repo.watchers_count = 20
        mock_repo.size = 1024
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_repo.updated_at = create_mock_datetime("2024-01-02")
        mock_repo.pushed_at = create_mock_datetime("2024-01-03")
        mock_repo.owner.login = f"{test_username}"
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/test-repo"})
        
        assert result.success
        assert result.output["repository"]["name"] == "test-repo"
        assert result.output["repository"]["full_name"] == f"{test_username}/test-repo"
        assert result.output["repository"]["stargazers_count"] == 42

    @pytest.mark.asyncio
    async def test_get_private_repository(self, test_username):
        """Test getting a private repository."""
        mock_repo = Mock()
        mock_repo.name = "private-repo"
        mock_repo.full_name = f"{test_username}/private-repo"
        mock_repo.private = True
        mock_repo.html_url = "https://github.com/{test_username}/private-repo"
        mock_repo.default_branch = "main"
        mock_repo.owner.login = f"{test_username}"
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/private-repo"})
        
        assert result.success
        assert result.output["repository"]["private"] is True

    @pytest.mark.asyncio
    async def test_get_fork_repository(self, test_username):
        """Test getting a forked repository."""
        mock_repo = Mock()
        mock_repo.name = "forked-repo"
        mock_repo.full_name = f"{test_username}/forked-repo"
        mock_repo.fork = True
        mock_repo.parent = Mock(full_name="original/repo")
        mock_repo.html_url = "https://github.com/{test_username}/forked-repo"
        mock_repo.default_branch = "main"
        mock_repo.owner.login = f"{test_username}"
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/forked-repo"})
        
        assert result.success
        assert result.output["repository"]["fork"] is True

    @pytest.mark.asyncio
    async def test_get_repository_not_found(self, test_username):
        """Test getting a non-existent repository."""
        self.manager.get_repository.side_effect = UnknownObjectException(404, "Not Found")

        result = await self.tool.execute({"repository": f"{test_username}/nonexistent"})
        
        assert not result.success


class TestListRepositoriesToolComprehensive:
    """Comprehensive tests for ListRepositoriesTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListRepositoriesTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_user_repositories(self, test_username):
        """Test listing repositories for a user."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "repo1"
        mock_repo.full_name = f"{test_username}/repo1"
        mock_repo.description = "Test repo"
        mock_repo.html_url = "https://github.com/{test_username}/repo1"
        mock_repo.private = False
        mock_repo.stargazers_count = 10
        mock_repo.fork = False
        mock_repo.archived = False
        mock_repo.language = "Python"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_repo.updated_at = create_mock_datetime("2024-01-01")
        mock_repo.pushed_at = create_mock_datetime("2024-01-01")
        mock_repo.watchers_count = 5
        mock_repo.forks_count = 2
        mock_repo.open_issues_count = 3
        mock_repo.id = 12345
        mock_user.get_repos.return_value = [mock_repo]
        self.manager.client = Mock()
        self.manager.client.get_organization.side_effect = GithubException(404, {"message": "Not Found"})
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({"owner": f"{test_username}"})
        
        assert result.success
        assert len(result.output["repositories"]) == 1
        assert result.output["repositories"][0]["name"] == "repo1"

    @pytest.mark.asyncio
    async def test_list_org_repositories(self, test_username):
        """Test listing repositories for an organization."""
        mock_org = Mock()
        mock_repo = Mock()
        mock_repo.name = "org-repo"
        mock_repo.full_name = "myorg/org-repo"
        mock_repo.description = "Organization repo"
        mock_repo.html_url = "https://github.com/myorg/org-repo"
        mock_repo.private = False
        mock_repo.stargazers_count = 50
        mock_repo.fork = False
        mock_repo.archived = False
        mock_repo.language = "Python"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_repo.updated_at = create_mock_datetime("2024-01-01")
        mock_repo.pushed_at = create_mock_datetime("2024-01-01")
        mock_repo.watchers_count = 5
        mock_repo.forks_count = 2
        mock_repo.open_issues_count = 3
        mock_repo.id = 12345
        mock_org.get_repos.return_value = [mock_repo]
        self.manager.client = Mock()
        self.manager.client.get_organization.return_value = mock_org

        result = await self.tool.execute({"owner": "myorg", "type": "org"})
        
        assert result.success
        assert len(result.output["repositories"]) == 1

    @pytest.mark.asyncio
    async def test_list_repositories_filter_type(self, test_username):
        """Test listing repositories filtered by type."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "public-repo"
        mock_repo.full_name = f"{test_username}/public-repo"
        mock_repo.private = False
        mock_repo.html_url = "https://github.com/{test_username}/public-repo"
        mock_user.get_repos.return_value = [mock_repo]
        self.manager.client = Mock()
        self.manager.client.get_organization.side_effect = GithubException(404, {"message": "Not Found"})
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({"owner": f"{test_username}", "type": "public"})
        
        assert result.success

    @pytest.mark.asyncio
    async def test_list_repositories_sorted(self, test_username):
        """Test listing repositories with sorting."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "sorted-repo"
        mock_repo.full_name = f"{test_username}/sorted-repo"
        mock_repo.html_url = "https://github.com/{test_username}/sorted-repo"
        mock_repo.private = False
        mock_user.get_repos.return_value = [mock_repo]
        self.manager.client = Mock()
        self.manager.client.get_organization.side_effect = GithubException(404, {"message": "Not Found"})
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({
            "owner": f"{test_username}",
            "sort": "updated",
            "direction": "desc"
        })
        
        assert result.success


class TestCreateRepositoryToolComprehensive:
    """Comprehensive tests for CreateRepositoryTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreateRepositoryTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_repository_basic(self, test_username):
        """Test creating a basic repository."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "new-repo"
        mock_repo.full_name = f"{test_username}/new-repo"
        mock_repo.html_url = "https://github.com/{test_username}/new-repo"
        mock_repo.private = False
        mock_repo.id = 12345
        mock_repo.description = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = f"{test_username}"
        mock_repo.clone_url = f"https://github.com/{test_username}/repo.git"
        mock_repo.ssh_url = f"git@github.com:{test_username}/repo.git"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_user.create_repo.return_value = mock_repo
        self.manager.client = Mock()
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({"name": "new-repo"})
        
        assert result.success
        assert result.output["repository"]["name"] == "new-repo"

    @pytest.mark.asyncio
    async def test_create_private_repository(self, test_username):
        """Test creating a private repository."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "private-repo"
        mock_repo.full_name = f"{test_username}/private-repo"
        mock_repo.html_url = "https://github.com/{test_username}/private-repo"
        mock_repo.private = True
        mock_repo.id = 12346
        mock_repo.description = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = f"{test_username}"
        mock_repo.clone_url = f"https://github.com/{test_username}/private-repo.git"
        mock_repo.ssh_url = f"git@github.com:{test_username}/private-repo.git"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_user.create_repo.return_value = mock_repo
        self.manager.client = Mock()
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({
            "name": "private-repo",
            "private": True
        })
        
        assert result.success
        assert result.output["repository"]["private"] is True

    @pytest.mark.asyncio
    async def test_create_repository_with_description(self, test_username):
        """Test creating a repository with description."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.id = 12345
        mock_repo.description = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = f"{test_username}"
        mock_repo.clone_url = f"https://github.com/{test_username}/repo.git"
        mock_repo.ssh_url = f"git@github.com:{test_username}/repo.git"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_repo.name = "described-repo"
        mock_repo.full_name = f"{test_username}/described-repo"
        mock_repo.description = "A great repository"
        mock_repo.html_url = "https://github.com/{test_username}/described-repo"
        mock_repo.private = False
        mock_user.create_repo.return_value = mock_repo
        self.manager.client = Mock()
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({
            "name": "described-repo",
            "description": "A great repository"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_repository_with_auto_init(self, test_username):
        """Test creating a repository with auto-init."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "initialized-repo"
        mock_repo.full_name = f"{test_username}/initialized-repo"
        mock_repo.html_url = "https://github.com/{test_username}/initialized-repo"
        mock_repo.private = False
        mock_repo.id = 12348
        mock_repo.description = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = f"{test_username}"
        mock_repo.clone_url = f"https://github.com/{test_username}/initialized-repo.git"
        mock_repo.ssh_url = f"git@github.com:{test_username}/initialized-repo.git"
        mock_repo.default_branch = "main"
        mock_repo.created_at = create_mock_datetime("2024-01-01")
        mock_user.create_repo.return_value = mock_repo
        self.manager.client = Mock()
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({
            "name": "initialized-repo",
            "auto_init": True
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_repository_name_exists(self, test_username):
        """Test creating a repository with existing name."""
        mock_user = Mock()
        mock_user.create_repo.side_effect = GithubException(422, {"message": "name already exists"})
        self.manager.client = Mock()
        self.manager.client.get_user.return_value = mock_user

        result = await self.tool.execute({"name": "existing-repo"})
        
        assert not result.success


class TestGetFileContentToolComprehensive:
    """Comprehensive tests for GetFileContentTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetFileContentTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_file_content_success(self, test_username):
        """Test successfully getting file content."""
        mock_repo = Mock()
        mock_content = Mock()
        mock_content.path = "README.md"
        mock_content.content = "IyBUZXN0IFJlYWRtZQ=="  # Base64 encoded "# Test Readme"
        mock_content.encoding = "base64"
        mock_content.size = 14
        mock_content.sha = "abc123"
        mock_repo.get_contents.return_value = mock_content
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "path": "README.md"
        })
        
        assert result.success
        assert result.output["file"]["path"] == "README.md"

    @pytest.mark.asyncio
    async def test_get_file_content_with_ref(self, test_username):
        """Test getting file content from specific ref."""
        mock_repo = Mock()
        mock_content = Mock()
        mock_content.path = "main.py"
        mock_content.content = "cHJpbnQoImhlbGxvIik="  # Base64 encoded
        mock_content.encoding = "base64"
        mock_repo.get_contents.return_value = mock_content
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "path": "main.py",
            "ref": "develop"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_get_file_not_found(self, test_username):
        """Test getting a non-existent file."""
        mock_repo = Mock()
        mock_repo.get_contents.side_effect = UnknownObjectException(404, "Not Found")
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "path": "nonexistent.txt"
        })
        
        assert not result.success


class TestListRepositoryContentsToolComprehensive:
    """Comprehensive tests for ListRepositoryContentsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListRepositoryContentsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_root_contents(self, test_username):
        """Test listing root directory contents."""
        mock_repo = Mock()
        mock_file = Mock()
        mock_file.name = "README.md"
        mock_file.path = "README.md"
        mock_file.type = "file"
        mock_file.size = 100
        mock_dir = Mock()
        mock_dir.name = "src"
        mock_dir.path = "src"
        mock_dir.type = "dir"
        mock_repo.get_contents.return_value = [mock_file, mock_dir]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["contents"]) == 2

    @pytest.mark.asyncio
    async def test_list_subdirectory_contents(self, test_username):
        """Test listing subdirectory contents."""
        mock_repo = Mock()
        mock_file = Mock()
        mock_file.name = "main.py"
        mock_file.path = "src/main.py"
        mock_file.type = "file"
        mock_file.size = 500
        mock_repo.get_contents.return_value = [mock_file]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "path": "src"
        })
        
        assert result.success
        assert result.output["contents"][0]["name"] == "main.py"

    @pytest.mark.asyncio
    async def test_list_contents_with_ref(self, test_username):
        """Test listing contents from specific ref."""
        mock_repo = Mock()
        mock_file = Mock()
        mock_file.name = "config.json"
        mock_file.path = "config.json"
        mock_file.type = "file"
        mock_repo.get_contents.return_value = [mock_file]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "ref": "feature-branch"
        })
        
        assert result.success
