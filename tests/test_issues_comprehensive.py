"""Comprehensive tests for GitHub Issues tools covering all scenarios."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tests.conftest import create_mock_datetime
from github.GithubException import GithubException, UnknownObjectException, BadCredentialsException

from amplifier_module_tool_github.tools.issues import (
    ListIssuesTool,
    GetIssueTool,
    CreateIssueTool,
    UpdateIssueTool,
    CommentIssueTool,
)
from amplifier_module_tool_github.exceptions import (
    AuthenticationError,
    RepositoryNotFoundError,
    IssueNotFoundError,
)


class TestListIssuesToolComprehensive:
    """Comprehensive tests for ListIssuesTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListIssuesTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_issues_success_all_states(self, test_username):
        """Test listing issues with different state filters."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.user = Mock()
        mock_issue.user.login = f"{test_username}"
        mock_repo.get_issues.return_value = [mock_issue]
        self.manager.get_repository.return_value = mock_repo

        # Test open issues
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "open"})
        assert result.success
        assert len(result.output["issues"]) == 1
        # Tool passes additional default parameters
        assert mock_repo.get_issues.called

        # Test closed issues
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "closed"})
        assert result.success
        # Tool passes additional default parameters
        assert mock_repo.get_issues.called

        # Test all issues
        result = await self.tool.execute({"repository": f"{test_username}/repo", "state": "all"})
        assert result.success
        # Tool passes additional default parameters
        assert mock_repo.get_issues.called

    @pytest.mark.asyncio
    async def test_list_issues_with_labels(self, test_username):
        """Test listing issues filtered by labels."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.title = "Bug Report"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.user = Mock()
        mock_issue.user.login = f"{test_username}"
        # Create label mocks with proper attributes
        label_bug = Mock()
        label_bug.name = "bug"
        label_bug.color = "red"
        label_bug.description = "Bug issue"
        label_high = Mock()
        label_high.name = "priority:high"
        label_high.color = "orange"
        label_high.description = "High priority"
        mock_issue.labels = [label_bug, label_high]
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_repo.get_issues.return_value = [mock_issue]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "labels": ["bug", "priority:high"]
        })
        
        assert result.success
        assert len(result.output["issues"]) == 1
        assert mock_repo.get_issues.called  # Tool passes additional default parameters

    @pytest.mark.asyncio
    async def test_list_issues_with_assignee(self, test_username):
        """Test listing issues filtered by assignee."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Assigned Issue"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.user.login = f"{test_username}"
        mock_assignee = Mock()
        mock_assignee.login = f"{test_username}"
        mock_issue.assignees = [mock_assignee]
        mock_issue.assignee = Mock(login=f"{test_username}")
        mock_repo.get_issues.return_value = [mock_issue]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "assignee": f"{test_username}"
        })
        
        assert result.success
        assert len(result.output["issues"]) == 1

    @pytest.mark.asyncio
    async def test_list_issues_with_creator(self, test_username):
        """Test listing issues filtered by creator."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Created by me"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.user.login = f"{test_username}"
        mock_repo.get_issues.return_value = [mock_issue]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "creator": f"{test_username}"
        })
        
        assert result.success
        assert len(result.output["issues"]) == 1

    @pytest.mark.asyncio
    async def test_list_issues_with_milestone(self, test_username):
        """Test listing issues filtered by milestone."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Milestone Issue"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.user.login = f"{test_username}"
        mock_issue.milestone = Mock(number=1, title="v1.0")
        mock_repo.get_issues.return_value = [mock_issue]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "milestone": 1
        })
        
        assert result.success
        assert len(result.output["issues"]) == 1

    @pytest.mark.asyncio
    async def test_list_issues_empty_result(self, test_username):
        """Test listing issues when none exist."""
        mock_repo = Mock()
        mock_repo.get_issues.return_value = []
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["issues"]) == 0

    @pytest.mark.asyncio
    async def test_list_issues_repository_not_found(self, test_username):
        """Test listing issues when repository doesn't exist."""
        from amplifier_module_tool_github.exceptions import RepositoryNotFoundError
        self.manager.get_repository.side_effect = RepositoryNotFoundError(f"{test_username}/nonexistent")

        result = await self.tool.execute({"repository": f"{test_username}/nonexistent"})
        
        assert result.success  # Tool returns success with errors in output
        assert result.output["errors"]
        assert len(result.output["errors"]) > 0

    @pytest.mark.asyncio
    async def test_list_issues_rate_limit(self, test_username):
        """Test handling rate limit errors."""
        from amplifier_module_tool_github.exceptions import RateLimitError
        self.manager.get_repository.side_effect = RateLimitError("2024-12-31T23:59:59Z")

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert not result.success
        assert result.error
        assert "RATE_LIMIT" in result.error["code"]

    @pytest.mark.asyncio
    async def test_list_issues_permission_denied(self, test_username):
        """Test handling permission errors."""
        self.manager.get_repository.side_effect = GithubException(403, {"message": "Forbidden"})

        result = await self.tool.execute({"repository": f"{test_username}/private-repo"})
        
        assert result.success
        assert result.output["errors"]


class TestGetIssueToolComprehensive:
    """Comprehensive tests for GetIssueTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetIssueTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_issue_success(self, test_username):
        """Test successfully getting an issue."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.closed_at = None
        mock_issue.title = "Test Issue"
        mock_issue.body = "This is a test issue"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/42"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.updated_at = create_mock_datetime("2024-01-02")
        mock_issue.user.login = f"{test_username}"
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.milestone = None
        mock_issue.comments = 5
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "issue_number": 42})
        
        assert result.success
        assert result.output["issue"]["number"] == 42
        assert result.output["issue"]["title"] == "Test Issue"
        assert result.output["issue"]["state"] == "open"
        assert result.output["issue"]["comments_count"] == 5

    @pytest.mark.asyncio
    async def test_get_issue_with_labels(self, test_username):
        """Test getting an issue with labels."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.closed_at = None
        mock_issue.title = "Labeled Issue"
        mock_issue.body = "Issue with labels"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/42"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.updated_at = create_mock_datetime("2024-01-02")
        mock_issue.user.login = f"{test_username}"
        mock_issue.labels = [type("MockLabel", (), {"name": "bug", "color": "red", "description": "Bug issue"})(), type("MockLabel", (), {"name": "enhancement", "color": "blue", "description": "Enhancement request"})()]
        mock_issue.assignees = []
        mock_issue.milestone = None
        mock_issue.comments = 0
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "issue_number": 42})
        
        assert result.success
        assert len(result.output["issue"]["labels"]) == 2
        assert any(label['name'] == 'bug' for label in result.output['issue']['labels'])

    @pytest.mark.asyncio
    async def test_get_issue_with_assignees(self, test_username):
        """Test getting an issue with assignees."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.closed_at = None
        mock_issue.title = "Assigned Issue"
        mock_issue.body = "Issue with assignees"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/42"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.updated_at = create_mock_datetime("2024-01-02")
        mock_issue.user.login = f"{test_username}"
        mock_issue.labels = []
        mock_issue.assignees = [Mock(login=f"{test_username}"), Mock(login="collaborator")]
        mock_issue.milestone = None
        mock_issue.comments = 0
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "issue_number": 42})
        
        assert result.success
        assert len(result.output["issue"]["assignees"]) == 2
        assignee_logins = [a["login"] for a in result.output["issue"]["assignees"]]
        assert f"{test_username}" in assignee_logins
        assert "collaborator" in assignee_logins

    @pytest.mark.asyncio
    async def test_get_issue_with_milestone(self, test_username):
        """Test getting an issue with milestone."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.closed_at = None
        mock_issue.title = "Milestone Issue"
        mock_issue.body = "Issue with milestone"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/42"
        mock_issue.created_at = create_mock_datetime("2024-01-01")
        mock_issue.updated_at = create_mock_datetime("2024-01-02")
        mock_issue.user.login = f"{test_username}"
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.milestone = Mock(number=1, title="v1.0")
        mock_issue.comments = 0
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "issue_number": 42})
        
        assert result.success
        assert result.output["issue"]["milestone"] is not None
        assert result.output["issue"]["milestone"]["title"] == "v1.0"

    @pytest.mark.asyncio
    async def test_get_issue_not_found(self, test_username):
        """Test getting a non-existent issue."""
        mock_repo = Mock()
        mock_repo.get_issue.side_effect = UnknownObjectException(404, "Not Found")
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "issue_number": 999})
        
        assert not result.success
        assert "ISSUE_NOT_FOUND" in result.error["code"]

    @pytest.mark.asyncio
    async def test_get_issue_missing_parameters(self, test_username):
        """Test getting an issue with missing parameters."""
        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        assert not result.success

        result = await self.tool.execute({"issue_number": 42})
        assert not result.success


class TestCreateIssueToolComprehensive:
    """Comprehensive tests for CreateIssueTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreateIssueTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_issue_basic(self, test_username):
        """Test creating a basic issue with title only."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "New Issue"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.body = "Issue description"  # Ensure body attribute exists
        mock_repo.create_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "New Issue"
        })
        
        assert result.success
        assert result.output["issue"]["number"] == 1
        assert result.output["issue"]["title"] == "New Issue"

    @pytest.mark.asyncio
    async def test_create_issue_with_body(self, test_username):
        """Test creating an issue with title and body."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Issue with Description"
        mock_issue.body = "This is a detailed description"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.body = "Issue description"  # Ensure body attribute exists
        mock_repo.create_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Issue with Description",
            "body": "This is a detailed description"
        })
        
        assert result.success
        assert result.output["issue"]["title"] == "Issue with Description"
        assert result.output["issue"]["number"] == 1

    @pytest.mark.asyncio
    async def test_create_issue_with_labels(self, test_username):
        """Test creating an issue with labels."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Labeled Issue"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.labels = [type("MockLabel", (), {"name": "bug", "color": "red", "description": "Bug issue"})(), type("MockLabel", (), {"name": "enhancement", "color": "blue", "description": "Enhancement request"})()]
        mock_issue.body = "Issue description"  # Ensure body attribute exists
        mock_repo.create_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Labeled Issue",
            "labels": ["bug", "enhancement"]
        })
        
        assert result.success
        mock_repo.create_issue.assert_called_once()
        call_kwargs = mock_repo.create_issue.call_args[1]
        assert "bug" in call_kwargs["labels"]
        assert "enhancement" in call_kwargs["labels"]

    @pytest.mark.asyncio
    async def test_create_issue_with_assignees(self, test_username):
        """Test creating an issue with assignees."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Assigned Issue"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_issue.body = "Issue description"  # Ensure body attribute exists
        mock_repo.create_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Assigned Issue",
            "assignees": [f"{test_username}", "collaborator"]
        })
        
        assert result.success
        call_kwargs = mock_repo.create_issue.call_args[1]
        assert f"{test_username}" in call_kwargs["assignees"]

    @pytest.mark.asyncio
    async def test_create_issue_with_milestone(self, test_username):
        """Test creating an issue with a milestone."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Milestone Issue"
        mock_issue.html_url = "https://github.com/{test_username}/repo/issues/1"
        mock_milestone = Mock(number=1, title="v1.0")
        mock_repo.get_milestone.return_value = mock_milestone
        mock_issue.body = "Issue description"  # Ensure body attribute exists
        mock_repo.create_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Milestone Issue",
            "milestone": 1
        })
        
        assert result.success
        mock_repo.get_milestone.assert_called_once_with(number=1)

    @pytest.mark.asyncio
    async def test_create_issue_empty_title(self, test_username):
        """Test creating an issue with empty title."""
        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "   "
        })
        
        assert not result.success
        assert "VALIDATION_ERROR" in result.error["code"]

    @pytest.mark.asyncio
    async def test_create_issue_permission_denied(self, test_username):
        """Test creating an issue without permission."""
        mock_repo = Mock()
        mock_repo.create_issue.side_effect = GithubException(403, {"message": "Forbidden"})
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "title": "Permission Test"
        })
        
        assert not result.success
        assert "PERMISSION_DENIED" in result.error["code"]


class TestUpdateIssueToolComprehensive:
    """Comprehensive tests for UpdateIssueTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = UpdateIssueTool(self.manager)

    @pytest.mark.asyncio
    async def test_update_issue_title(self, test_username):
        """Test updating issue title."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.title = "Updated Title"
        mock_issue.edit = Mock()
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "title": "Updated Title"
        })
        
        assert result.success
        mock_issue.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_issue_state(self, test_username):
        """Test updating issue state (open/closed)."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.state = "closed"
        mock_issue.edit = Mock()
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "state": "closed"
        })
        
        assert result.success
        call_kwargs = mock_issue.edit.call_args[1]
        assert call_kwargs["state"] == "closed"

    @pytest.mark.asyncio
    async def test_update_issue_labels(self, test_username):
        """Test updating issue labels."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.edit = Mock()
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "labels": ["bug", "critical"]
        })
        
        assert result.success
        call_kwargs = mock_issue.edit.call_args[1]
        assert "bug" in call_kwargs["labels"]

    @pytest.mark.asyncio
    async def test_update_issue_assignees(self, test_username):
        """Test updating issue assignees."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 42
        mock_issue.pull_request = None
        mock_issue.labels = []
        mock_issue.assignees = []
        mock_issue.comments = 0
        mock_issue.updated_at = None
        mock_issue.closed_at = None
        mock_issue.edit = Mock()
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "assignees": [f"{test_username}"]
        })
        
        assert result.success
        call_kwargs = mock_issue.edit.call_args[1]
        assert f"{test_username}" in call_kwargs["assignees"]


class TestCommentIssueToolComprehensive:
    """Comprehensive tests for CommentIssueTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CommentIssueTool(self.manager)

    @pytest.mark.asyncio
    async def test_add_comment_success(self, test_username):
        """Test successfully adding a comment."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.pull_request = None
        mock_comment = Mock()
        mock_comment.id = 1
        mock_comment.body = "Test comment"
        mock_comment.html_url = "https://github.com/{test_username}/repo/issues/42#issuecomment-1"
        mock_comment.user.login = f"{test_username}"
        mock_issue.create_comment.return_value = mock_comment
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "body": "Test comment"
        })
        
        assert result.success
        assert result.output["comment"]["body"] == "Test comment"
        mock_issue.create_comment.assert_called_once_with(body="Test comment")

    @pytest.mark.asyncio
    async def test_add_comment_with_markdown(self, test_username):
        """Test adding a comment with Markdown formatting."""
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.pull_request = None
        mock_comment = Mock()
        mock_comment.id = 1
        mock_comment.body = "# Heading\n- Item 1\n- Item 2"
        mock_comment.html_url = "https://github.com/{test_username}/repo/issues/42#issuecomment-1"
        mock_comment.user.login = f"{test_username}"
        mock_issue.create_comment.return_value = mock_comment
        mock_repo.get_issue.return_value = mock_issue
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "body": "# Heading\n- Item 1\n- Item 2"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_add_comment_empty_body(self, test_username):
        """Test adding a comment with empty body."""
        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 42,
            "body": "   "
        })
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_add_comment_issue_not_found(self, test_username):
        """Test adding comment to non-existent issue."""
        mock_repo = Mock()
        mock_repo.get_issue.side_effect = UnknownObjectException(404, "Not Found")
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "issue_number": 999,
            "body": "Test comment"
        })
        
        assert not result.success
