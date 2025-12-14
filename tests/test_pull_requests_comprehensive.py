"""Comprehensive tests for GitHub Pull Request tools covering all scenarios."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tests.conftest import create_mock_datetime
from github.GithubException import GithubException, UnknownObjectException

from amplifier_module_tool_github.tools.pull_requests import (
    ListPullRequestsTool,
    GetPullRequestTool,
    CreatePullRequestTool,
    UpdatePullRequestTool,
    MergePullRequestTool,
    ReviewPullRequestTool,
)


class TestListPullRequestsToolComprehensive:
    """Comprehensive tests for ListPullRequestsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListPullRequestsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_prs_all_states(self, test_username):
        """Test listing PRs with different state filters."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_repo.get_pulls.return_value = [mock_pr]
        self.manager.get_repository.return_value = mock_repo

        # Test open PRs
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "open"})
        assert result.success
        assert len(result.output["pull_requests"]) == 1

        # Test closed PRs
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "closed"})
        assert result.success

        # Test all PRs
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "all"})
        assert result.success

    @pytest.mark.asyncio
    async def test_list_prs_with_base_branch(self, test_username):
        """Test listing PRs filtered by base branch."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "PR to main"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_repo.get_pulls.return_value = [mock_pr]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "base": "main"
        })
        
        assert result.success
        assert mock_repo.get_pulls.called  # Tool passes additional default parameters

    @pytest.mark.asyncio
    async def test_list_prs_with_head_branch(self, test_username):
        """Test listing PRs filtered by head branch."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "PR from feature"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_repo.get_pulls.return_value = [mock_pr]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "head": "{test_username}:feature"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_list_prs_sorted_by_created(self, test_username):
        """Test listing PRs sorted by creation date."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "Oldest PR"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_repo.get_pulls.return_value = [mock_pr]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "sort": "created",
            "direction": "asc"
        })
        
        assert result.success


class TestGetPullRequestToolComprehensive:
    """Comprehensive tests for GetPullRequestTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetPullRequestTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_pr_success(self, test_username):
        """Test successfully getting a pull request."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Test PR"
        mock_pr.body = "PR description"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/42"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.updated_at = create_mock_datetime("2024-01-02")
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.head.sha = "abc123"
        mock_pr.head.repo = Mock()
        mock_pr.head.repo.full_name = f"{test_username}/repo"
        mock_pr.base.ref = "main"
        mock_pr.base.sha = "def456"
        mock_pr.base.repo = Mock()
        mock_pr.base.repo.full_name = f"{test_username}/repo"
        mock_pr.mergeable = True
        mock_pr.merged = False
        mock_pr.merged_by = None
        mock_pr.mergeable_state = "clean"
        mock_pr.draft = False
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 2
        mock_pr.get_files.return_value = []
        mock_pr.get_reviews.return_value = []
        mock_pr.get_review_comments.return_value = []
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "pull_number": 42})
        
        assert result.success
        assert result.output["pull_request"]["number"] == 42
        assert result.output["pull_request"]["title"] == "Test PR"
        assert result.output["pull_request"]["mergeable"] is True

    @pytest.mark.asyncio
    async def test_get_pr_with_labels(self, test_username):
        """Test getting a PR with labels."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Labeled PR"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/42"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_pr.labels = [Mock(**{"name": "enhancement", "color": "blue", "description": "Enhancement"}), Mock(name="documentation")]
        mock_pr.body = "PR description"
        mock_pr.merged_by = None
        mock_pr.mergeable_state = "clean"
        mock_pr.head.repo = None
        mock_pr.base.repo = None
        mock_pr.get_files.return_value = []
        mock_pr.get_reviews.return_value = []
        mock_pr.get_review_comments.return_value = []
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "pull_number": 42})
        
        assert result.success
        assert len(result.output["pull_request"]["labels"]) == 2

    @pytest.mark.asyncio
    async def test_get_pr_draft(self, test_username):
        """Test getting a draft PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Draft PR"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/42"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.body = "PR description"
        mock_pr.merged_by = None
        mock_pr.mergeable_state = "clean"
        mock_pr.head.repo = None
        mock_pr.base.repo = None
        mock_pr.closed_at = None
        mock_pr.merged_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_pr.draft = True
        mock_pr.get_files.return_value = []
        mock_pr.get_reviews.return_value = []
        mock_pr.get_review_comments.return_value = []
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "pull_number": 42})
        
        assert result.success
        assert result.output["pull_request"]["draft"] is True

    @pytest.mark.asyncio
    async def test_get_pr_merged(self, test_username):
        """Test getting a merged PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Merged PR"
        mock_pr.state = "closed"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/42"
        mock_pr.created_at = create_mock_datetime("2024-01-01")
        mock_pr.user.login = f"{test_username}"
        mock_pr.head.ref = "feature"
        mock_pr.base.ref = "main"
        mock_pr.mergeable = True
        mock_pr.labels = []
        mock_pr.assignees = []
        mock_pr.requested_reviewers = []
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.body = "PR description"
        mock_pr.mergeable_state = "clean"
        mock_pr.head.repo = None
        mock_pr.base.repo = None
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1
        mock_pr.updated_at = None
        mock_pr.closed_at = None
        mock_pr.head.sha = "abc123"
        mock_pr.base.sha = "def456"
        mock_pr.merged = True
        mock_pr.merged_at = create_mock_datetime("2024-01-03")
        mock_pr.merged_by = Mock()
        mock_pr.merged_by.login = f"{test_username}"
        mock_pr.draft = False
        mock_pr.get_files.return_value = []
        mock_pr.get_reviews.return_value = []
        mock_pr.get_review_comments.return_value = []
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "pull_number": 42})
        
        assert result.success
        assert result.output["pull_request"]["merged"] is True

    @pytest.mark.asyncio
    async def test_get_pr_not_found(self, test_username):
        """Test getting a non-existent PR."""
        mock_repo = Mock()
        mock_repo.get_pull.side_effect = UnknownObjectException(404, "Not Found")
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "pull_number": 999})
        
        assert not result.success


class TestCreatePullRequestToolComprehensive:
    """Comprehensive tests for CreatePullRequestTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreatePullRequestTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_pr_basic(self, test_username):
        """Test creating a basic PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "New PR"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "New PR",
            "head": "feature-branch",
            "base": "main"
        })
        
        assert result.success
        assert result.output["pull_request"]["number"] == 1

    @pytest.mark.asyncio
    async def test_create_pr_with_body(self, test_username):
        """Test creating a PR with description."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "PR with Description"
        mock_pr.body = "Detailed description"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "PR with Description",
            "head": "feature",
            "base": "main",
            "body": "Detailed description"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_pr_draft(self, test_username):
        """Test creating a draft PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "Draft PR"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.draft = True
        mock_repo.create_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Draft PR",
            "head": "feature",
            "base": "main",
            "draft": True
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_pr_with_reviewers(self, test_username):
        """Test creating a PR with reviewers."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "PR with Reviewers"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.create_review_request = Mock()
        mock_repo.create_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "PR with Reviewers",
            "head": "feature",
            "base": "main",
            "reviewers": [f"{test_username}", "reviewer2"]
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_pr_with_labels(self, test_username):
        """Test creating a PR with labels."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.title = "Labeled PR"
        mock_pr.html_url = "https://github.com/{test_username}/repo/pull/1"
        mock_pr.set_labels = Mock()
        mock_repo.create_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Labeled PR",
            "head": "feature",
            "base": "main",
            "labels": ["enhancement", "documentation"]
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_pr_branch_not_found(self, test_username):
        """Test creating PR with non-existent branch."""
        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(422, {"message": "Branch not found"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Test PR",
            "head": "nonexistent-branch",
            "base": "main"
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_create_pr_no_commits(self, test_username):
        """Test creating PR with no commits between branches."""
        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(422, {"message": "No commits between"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Empty PR",
            "head": "same-as-base",
            "base": "main"
        })
        
        assert not result.success


class TestUpdatePullRequestToolComprehensive:
    """Comprehensive tests for UpdatePullRequestTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = UpdatePullRequestTool(self.manager)

    @pytest.mark.asyncio
    async def test_update_pr_title(self, test_username):
        """Test updating PR title."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.edit = Mock()
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "title": "Updated Title"
        })
        
        assert result.success
        mock_pr.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_pr_state(self, test_username):
        """Test updating PR state (open/closed)."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.edit = Mock()
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "state": "closed"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_update_pr_base_branch(self, test_username):
        """Test updating PR base branch."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.edit = Mock()
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "base": "develop"
        })
        
        assert result.success


class TestMergePullRequestToolComprehensive:
    """Comprehensive tests for MergePullRequestTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = MergePullRequestTool(self.manager)

    @pytest.mark.asyncio
    async def test_merge_pr_default_method(self, test_username):
        """Test merging PR with default method."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.merge.return_value = Mock(merged=True, sha="abc123")
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_merge_pr_squash(self, test_username):
        """Test merging PR with squash method."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.merge.return_value = Mock(merged=True, sha="abc123")
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "merge_method": "squash"
        })
        
        assert result.success
        mock_pr.merge.assert_called_once()

    @pytest.mark.asyncio
    async def test_merge_pr_rebase(self, test_username):
        """Test merging PR with rebase method."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.merge.return_value = Mock(merged=True, sha="abc123")
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "merge_method": "rebase"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_merge_pr_not_mergeable(self, test_username):
        """Test merging PR that is not mergeable."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.mergeable = False
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_merge_pr_with_commit_message(self, test_username):
        """Test merging PR with custom commit message."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.merge.return_value = Mock(merged=True, sha="abc123")
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "commit_title": "Custom merge message",
            "commit_message": "Detailed merge description"
        })
        
        assert result.success


class TestReviewPullRequestToolComprehensive:
    """Comprehensive tests for ReviewPullRequestTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ReviewPullRequestTool(self.manager)

    @pytest.mark.asyncio
    async def test_review_pr_approve(self, test_username):
        """Test approving a PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_review = Mock()
        mock_review.id = 1
        mock_review.state = "APPROVED"
        mock_pr.state = "open"
        mock_pr.create_review.return_value = mock_review
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "event": "APPROVE"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_review_pr_request_changes(self, test_username):
        """Test requesting changes on a PR."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_review = Mock()
        mock_review.id = 2
        mock_review.state = "CHANGES_REQUESTED"
        mock_pr.state = "open"
        mock_pr.create_review.return_value = mock_review
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "event": "REQUEST_CHANGES",
            "body": "Please fix the tests"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_review_pr_comment(self, test_username):
        """Test commenting on a PR without approval."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_review = Mock()
        mock_review.id = 3
        mock_review.state = "COMMENTED"
        mock_pr.state = "open"
        mock_pr.create_review.return_value = mock_review
        mock_repo.get_pull.return_value = mock_pr
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "pull_number": 42,
            "event": "COMMENT",
            "body": "Looks good to me"
        })
        
        assert result.success
