"""Comprehensive tests for GitHub Branches, Commits, and Tags tools."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tests.conftest import create_mock_datetime
from github.GithubException import GithubException, UnknownObjectException

from amplifier_module_tool_github.tools.branches import (
    ListBranchesTool,
    GetBranchTool,
    CreateBranchTool,
    CompareBranchesTool,
)
from amplifier_module_tool_github.tools.commits import (
    ListCommitsTool,
    GetCommitTool,
)


class TestListBranchesToolComprehensive:
    """Comprehensive tests for ListBranchesTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListBranchesTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_branches_success(self, test_username):
        """Test successfully listing branches."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_branch.name = "main"
        mock_branch.commit.sha = "abc123"
        mock_branch.protected = False
        mock_repo.get_branches.return_value = [mock_branch]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["branches"]) == 1
        assert result.output["branches"][0]["name"] == "main"

    @pytest.mark.asyncio
    async def test_list_branches_multiple(self, test_username):
        """Test listing multiple branches."""
        mock_repo = Mock()
        mock_main = Mock()
        mock_main.name = "main"
        mock_main.commit.sha = "abc123"
        mock_main.protected = True
        mock_develop = Mock()
        mock_develop.name = "develop"
        mock_develop.commit.sha = "def456"
        mock_develop.protected = False
        mock_feature = Mock()
        mock_feature.name = "feature/new-feature"
        mock_feature.commit.sha = "ghi789"
        mock_feature.protected = False
        mock_repo.get_branches.return_value = [mock_main, mock_develop, mock_feature]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["branches"]) == 3

    @pytest.mark.asyncio
    async def test_list_branches_protected(self, test_username):
        """Test listing branches with protection status."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_branch.name = "main"
        mock_branch.commit.sha = "abc123"
        mock_branch.protected = True
        mock_repo.get_branches.return_value = [mock_branch]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert result.output["branches"][0]["protected"] is True


class TestGetBranchToolComprehensive:
    """Comprehensive tests for GetBranchTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetBranchTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_branch_success(self, test_username):
        """Test successfully getting branch details."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_branch.name = "main"
        mock_branch.commit.sha = "abc123"
        mock_branch.commit.commit.message = "Initial commit"
        mock_branch.commit.commit.author.name = f"{test_username}"
        mock_branch.protected = True
        mock_repo.get_branch.return_value = mock_branch
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "main"
        })
        
        assert result.success
        assert result.output["branch"]["name"] == "main"
        assert result.output["branch"]["protected"] is True

    @pytest.mark.asyncio
    async def test_get_branch_not_found(self, test_username):
        """Test getting a non-existent branch."""
        mock_repo = Mock()
        mock_repo.get_branch.side_effect = GithubException(404, {"message": "Branch not found"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "nonexistent"
        })
        
        assert not result.success


class TestCreateBranchToolComprehensive:
    """Comprehensive tests for CreateBranchTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreateBranchTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_branch_from_default(self, test_username):
        """Test creating branch from default branch."""
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_main_branch = Mock()
        mock_main_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_main_branch
        mock_ref = Mock()
        mock_ref.ref = "refs/heads/new-feature"
        mock_repo.create_git_ref.return_value = mock_ref
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "new-feature"
        })
        
        assert result.success
        mock_repo.create_git_ref.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_branch_from_sha(self, test_username):
        """Test creating branch from specific SHA."""
        mock_repo = Mock()
        mock_ref = Mock()
        mock_ref.ref = "refs/heads/feature-from-sha"
        mock_repo.create_git_ref.return_value = mock_ref
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "feature-from-sha",
            "sha": "def456"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_branch_from_ref(self, test_username):
        """Test creating branch from another ref."""
        mock_repo = Mock()
        mock_source_branch = Mock()
        mock_source_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_source_branch
        mock_ref = Mock()
        mock_ref.ref = "refs/heads/feature-copy"
        mock_repo.create_git_ref.return_value = mock_ref
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "feature-copy",
            "from_branch": "develop"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_branch_already_exists(self, test_username):
        """Test creating branch that already exists."""
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_main_branch = Mock()
        mock_main_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_main_branch
        mock_repo.create_git_ref.side_effect = GithubException(422, {"message": "Reference already exists"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "branch": "existing-branch"
        })
        
        assert not result.success


class TestCompareBranchesToolComprehensive:
    """Comprehensive tests for CompareBranchesTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CompareBranchesTool(self.manager)

    @pytest.mark.asyncio
    async def test_compare_branches_success(self, test_username):
        """Test successfully comparing branches."""
        mock_repo = Mock()
        mock_comparison = Mock()
        mock_comparison.ahead_by = 5
        mock_comparison.behind_by = 2
        mock_comparison.total_commits = 5
        mock_comparison.status = "ahead"
        
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Test commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/test/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_comparison.commits = [mock_commit]
        
        mock_file = Mock()
        mock_file.filename = "test.py"
        mock_file.status = "modified"
        mock_file.additions = 10
        mock_file.deletions = 5
        mock_file.changes = 15
        mock_comparison.files = [mock_file]
        
        mock_repo.compare.return_value = mock_comparison
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "base": "main",
            "head": "feature"
        })
        
        assert result.success
        assert result.output["comparison"]["ahead_by"] == 5
        assert result.output["comparison"]["behind_by"] == 2

    @pytest.mark.asyncio
    async def test_compare_branches_identical(self, test_username):
        """Test comparing identical branches."""
        mock_repo = Mock()
        mock_comparison = Mock()
        mock_comparison.ahead_by = 0
        mock_comparison.behind_by = 0
        mock_comparison.total_commits = 0
        mock_comparison.status = "identical"
        mock_comparison.commits = []
        mock_comparison.files = []
        mock_repo.compare.return_value = mock_comparison
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "base": "main",
            "head": "main"
        })
        
        assert result.success
        assert result.output["comparison"]["status"] == "identical"

    @pytest.mark.asyncio
    async def test_compare_branches_diverged(self, test_username):
        """Test comparing diverged branches."""
        mock_repo = Mock()
        mock_comparison = Mock()
        mock_comparison.ahead_by = 3
        mock_comparison.behind_by = 4
        mock_comparison.total_commits = 3
        mock_comparison.status = "diverged"
        mock_comparison.commits = []
        mock_comparison.files = []
        mock_repo.compare.return_value = mock_comparison
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "base": "main",
            "head": "feature"
        })
        
        assert result.success
        assert result.output["comparison"]["status"] == "diverged"


class TestListCommitsToolComprehensive:
    """Comprehensive tests for ListCommitsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListCommitsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_commits_success(self, test_username):
        """Test successfully listing commits."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Test commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.email = "{test_username}@example.com"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_repo.get_commits.return_value = [mock_commit]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["commits"]) == 1
        assert result.output["commits"][0]["sha"] == "abc123"

    @pytest.mark.asyncio
    async def test_list_commits_with_sha(self, test_username):
        """Test listing commits from specific SHA."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "def456"
        mock_commit.commit.message = "Later commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-02")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/def456"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_repo.get_commits.return_value = [mock_commit]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sha": "def456"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_list_commits_with_path(self, test_username):
        """Test listing commits for specific path."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Updated README"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_repo.get_commits.return_value = [mock_commit]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "path": "README.md"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_list_commits_with_author(self, test_username):
        """Test listing commits by specific author."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "My commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_repo.get_commits.return_value = [mock_commit]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "author": f"{test_username}"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_list_commits_date_range(self, test_username):
        """Test listing commits within date range."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Recent commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-15")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_repo.get_commits.return_value = [mock_commit]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "since": "2024-01-01",
            "until": "2024-01-31"
        })
        
        assert result.success


class TestGetCommitToolComprehensive:
    """Comprehensive tests for GetCommitTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetCommitTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_commit_success(self, test_username):
        """Test successfully getting commit details."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Test commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.email = "{test_username}@example.com"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_commit.stats.additions = 50
        mock_commit.stats.deletions = 20
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_commit.stats.total = 70
        
        mock_file = Mock()
        mock_file.filename = "test.py"
        mock_file.status = "modified"
        mock_file.additions = 30
        mock_file.deletions = 10
        mock_file.changes = 40
        mock_commit.files = [mock_file]
        
        mock_repo.get_commit.return_value = mock_commit
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sha": "abc123"
        })
        
        assert result.success
        assert result.output["commit"]["sha"] == "abc123"
        assert result.output["commit"]["stats"]["additions"] == 50

    @pytest.mark.asyncio
    async def test_get_commit_with_files(self, test_username):
        """Test getting commit with file changes."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Multi-file commit"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/abc123"
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        mock_commit.stats.total = 100
        
        mock_file1 = Mock()
        mock_file1.filename = "file1.py"
        mock_file1.status = "added"
        mock_file2 = Mock()
        mock_file2.filename = "file2.py"
        mock_file2.status = "modified"
        mock_file3 = Mock()
        mock_file3.filename = "file3.py"
        mock_file3.status = "deleted"
        mock_commit.files = [mock_file1, mock_file2, mock_file3]
        
        mock_repo.get_commit.return_value = mock_commit
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sha": "abc123"
        })
        
        assert result.success
        assert len(result.output["commit"]["files"]) == 3

    @pytest.mark.asyncio
    async def test_get_commit_not_found(self, test_username):
        """Test getting a non-existent commit."""
        mock_repo = Mock()
        mock_repo.get_commit.side_effect = GithubException(404, {"message": "Not Found"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sha": "nonexistent"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_get_commit_merge(self, test_username):
        """Test getting a merge commit."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.sha = "merge123"
        mock_commit.commit.message = "Merge branch 'feature' into main"
        mock_commit.commit.author.name = f"{test_username}"
        mock_commit.commit.author.date = create_mock_datetime("2024-01-01")
        mock_commit.commit.committer = mock_commit.commit.author
        mock_commit.html_url = "https://github.com/{test_username}/repo/commit/merge123"
        mock_commit.stats.total = 0
        mock_commit.files = []
        mock_commit.stats = Mock()
        mock_commit.stats.total = 0
        mock_commit.stats.additions = 0
        mock_commit.stats.deletions = 0
        mock_commit.parents = []
        mock_commit.committer = None
        mock_commit.commit.comment_count = 0
        
        mock_parent1 = Mock()
        mock_parent1.sha = "abc123"
        mock_parent2 = Mock()
        mock_parent2.sha = "def456"
        mock_commit.parents = [mock_parent1, mock_parent2]
        
        mock_repo.get_commit.return_value = mock_commit
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sha": "merge123"
        })
        
        assert result.success
        assert len(result.output["commit"]["parents"]) == 2
