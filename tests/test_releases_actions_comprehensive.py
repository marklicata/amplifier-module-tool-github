"""Comprehensive tests for GitHub Releases and Actions tools."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tests.conftest import create_mock_datetime
from github.GithubException import GithubException, UnknownObjectException

from amplifier_module_tool_github.tools.releases import (
    ListReleasesTool,
    GetReleaseTool,
    CreateReleaseTool,
    ListTagsTool,
    CreateTagTool,
)
from amplifier_module_tool_github.tools.actions import (
    ListWorkflowsTool,
    GetWorkflowTool,
    TriggerWorkflowTool,
    ListWorkflowRunsTool,
    GetWorkflowRunTool,
    CancelWorkflowRunTool,
    RerunWorkflowTool,
)


class TestListReleasesToolComprehensive:
    """Comprehensive tests for ListReleasesTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListReleasesTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_releases_success(self, test_username):
        """Test successfully listing releases."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "Version 1.0.0"
        mock_release.body = "Release notes"
        mock_release.draft = False
        mock_release.prerelease = False
        mock_release.created_at = create_mock_datetime("2024-01-01")
        mock_release.published_at = create_mock_datetime("2024-01-01")
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0"
        mock_release.author.login = f"{test_username}"
        mock_release.target_commitish = "main"
        mock_release.get_assets = Mock(return_value=[])
        mock_repo.get_releases.return_value = [mock_release]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["releases"]) == 1
        assert result.output["releases"][0]["tag_name"] == "v1.0.0"

    @pytest.mark.asyncio
    async def test_list_releases_with_drafts(self, test_username):
        """Test listing releases including drafts."""
        from datetime import datetime
        mock_repo = Mock()
        mock_draft = Mock()
        mock_draft.id = 1
        mock_draft.tag_name = "v2.0.0"
        mock_draft.title = "Version 2.0.0 Draft"
        mock_draft.name = "Version 2.0.0 Draft"
        mock_draft.body = "Draft release body"
        mock_draft.draft = True
        mock_draft.prerelease = False
        mock_draft.html_url = "https://github.com/{test_username}/repo/releases/tag/v2.0.0"
        mock_draft.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_draft.published_at = None
        mock_draft.target_commitish = "main"
        mock_draft.author.login = f"{test_username}"
        mock_draft.get_assets.return_value = []
        mock_repo.get_releases.return_value = [mock_draft]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "include_drafts": True})
        
        assert result.success
        assert result.output["releases"][0]["draft"] is True

    @pytest.mark.asyncio
    async def test_list_releases_with_prereleases(self, test_username):
        """Test listing releases including prereleases."""
        from datetime import datetime
        mock_repo = Mock()
        mock_prerelease = Mock()
        mock_prerelease.id = 1
        mock_prerelease.tag_name = "v1.0.0-beta"
        mock_prerelease.title = "Version 1.0.0 Beta"
        mock_prerelease.name = "Version 1.0.0 Beta"
        mock_prerelease.body = "Beta release body"
        mock_prerelease.draft = False
        mock_prerelease.prerelease = True
        mock_prerelease.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0-beta"
        mock_prerelease.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_prerelease.published_at = datetime(2024, 1, 2, 12, 0, 0)
        mock_prerelease.target_commitish = "main"
        mock_prerelease.author.login = f"{test_username}"
        mock_prerelease.get_assets.return_value = []
        mock_repo.get_releases.return_value = [mock_prerelease]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "include_prereleases": True})
        
        assert result.success
        assert result.output["releases"][0]["prerelease"] is True


class TestGetReleaseToolComprehensive:
    """Comprehensive tests for GetReleaseTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetReleaseTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_release_by_tag(self, test_username):
        """Test getting release by tag name."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "Version 1.0.0"
        mock_release.body = "Release notes"
        mock_release.draft = False
        mock_release.prerelease = False
        mock_release.created_at = create_mock_datetime("2024-01-01")
        mock_release.published_at = create_mock_datetime("2024-01-01")
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0"
        mock_release.author.login = f"{test_username}"
        mock_release.target_commitish = "main"
        mock_release.title = "Version 1.0.0"
        mock_release.tarball_url = "https://test/tarball"
        mock_release.zipball_url = "https://test/zipball"
        mock_release.get_assets = Mock(return_value=[])
        mock_release.assets = []
        mock_repo.get_release.return_value = mock_release  # Changed from get_release_by_tag_name
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v1.0.0"
        })
        
        assert result.success
        assert result.output["release"]["tag_name"] == "v1.0.0"

    @pytest.mark.asyncio
    async def test_get_release_by_id(self, test_username):
        """Test getting release by ID."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 12345
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "Version 1.0.0"
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/12345"
        mock_release.author.login = f"{test_username}"
        mock_release.target_commitish = "main"
        mock_release.id = 1
        mock_release.title = "Version 2.0.0"
        mock_release.tarball_url = "https://test/tarball"
        mock_release.zipball_url = "https://test/zipball"
        mock_release.get_assets = Mock(return_value=[])
        mock_release.assets = []
        mock_repo.get_latest_release.return_value = mock_release
        mock_release.created_at = create_mock_datetime("2024-01-01")
        mock_release.published_at = create_mock_datetime("2024-01-01")
        mock_release.title = "Version 1.0.0"
        mock_release.tarball_url = "https://test/tarball"
        mock_release.zipball_url = "https://test/zipball"
        mock_release.get_assets = Mock(return_value=[])
        mock_release.assets = []
        mock_repo.get_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "release_id": 12345
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_get_latest_release(self, test_username):
        """Test getting latest release."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v2.0.0"
        mock_release.name = "Latest Release"
        mock_release.title = "Latest Release"
        mock_release.body = "Release notes"
        mock_release.draft = False
        mock_release.prerelease = False
        mock_release.created_at = create_mock_datetime("2024-01-01")
        mock_release.published_at = create_mock_datetime("2024-01-01")
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/latest"
        mock_release.author.login = f"{test_username}"
        mock_release.target_commitish = "main"
        mock_release.tarball_url = "https://test/tarball"
        mock_release.zipball_url = "https://test/zipball"
        mock_release.get_assets = Mock(return_value=[])
        mock_release.assets = []
        mock_repo.get_latest_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo", "tag_name": "latest"})
        
        assert result.success
        assert result.output["release"]["tag_name"] == "v2.0.0"

    @pytest.mark.asyncio
    async def test_get_release_with_assets(self, test_username):
        """Test getting release with assets."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "Version 1.0.0"
        mock_release.title = "Version 1.0.0"
        mock_release.body = "Release notes"
        mock_release.draft = False
        mock_release.prerelease = False
        mock_release.created_at = create_mock_datetime("2024-01-01")
        mock_release.published_at = create_mock_datetime("2024-01-01")
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0"
        mock_release.author.login = f"{test_username}"
        mock_release.target_commitish = "main"
        mock_release.tarball_url = "https://test/tarball"
        mock_release.zipball_url = "https://test/zipball"
        
        mock_asset = Mock()
        mock_asset.id = 1
        mock_asset.name = "app.zip"
        mock_asset.label = "Application"
        mock_asset.size = 1024000
        mock_asset.download_count = 50
        mock_asset.content_type = "application/zip"
        mock_asset.state = "uploaded"
        mock_asset.created_at = create_mock_datetime("2024-01-01")
        mock_asset.updated_at = create_mock_datetime("2024-01-01")
        mock_asset.browser_download_url = "https://github.com/{test_username}/repo/releases/download/v1.0.0/app.zip"
        
        mock_release.get_assets = Mock(return_value=[mock_asset])
        mock_release.assets = [mock_asset]
        
        mock_repo.get_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v1.0.0"
        })
        
        assert result.success
        assert len(result.output["release"]["assets"]) == 1


class TestCreateReleaseToolComprehensive:
    """Comprehensive tests for CreateReleaseTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreateReleaseTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_release_basic(self, test_username):
        """Test creating a basic release."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "v1.0.0"
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0"
        mock_repo.create_git_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v1.0.0"
        })
        
        assert result.success
        assert result.output["release"]["tag_name"] == "v1.0.0"

    @pytest.mark.asyncio
    async def test_create_release_with_body(self, test_username):
        """Test creating a release with release notes."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0"
        mock_release.name = "Version 1.0.0"
        mock_release.body = "# Release Notes\n- Feature 1\n- Bug fix 2"
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0"
        mock_repo.create_git_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
            "body": "# Release Notes\n- Feature 1\n- Bug fix 2"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_draft_release(self, test_username):
        """Test creating a draft release."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v2.0.0"
        mock_release.draft = True
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v2.0.0"
        mock_repo.create_git_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v2.0.0",
            "draft": True
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_create_prerelease(self, test_username):
        """Test creating a prerelease."""
        mock_repo = Mock()
        mock_release = Mock()
        mock_release.id = 1
        mock_release.tag_name = "v1.0.0-beta"
        mock_release.prerelease = True
        mock_release.html_url = "https://github.com/{test_username}/repo/releases/tag/v1.0.0-beta"
        mock_repo.create_git_release.return_value = mock_release
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag_name": "v1.0.0-beta",
            "prerelease": True
        })
        
        assert result.success


class TestListTagsToolComprehensive:
    """Comprehensive tests for ListTagsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListTagsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_tags_success(self, test_username):
        """Test successfully listing tags."""
        mock_repo = Mock()
        mock_tag = Mock()
        mock_tag.name = "v1.0.0"
        mock_tag.commit.sha = "abc123"
        mock_repo.get_tags.return_value = [mock_tag]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["tags"]) == 1
        assert result.output["tags"][0]["name"] == "v1.0.0"


class TestCreateTagToolComprehensive:
    """Comprehensive tests for CreateTagTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CreateTagTool(self.manager)

    @pytest.mark.asyncio
    async def test_create_tag_success(self, test_username):
        """Test successfully creating a tag."""
        mock_repo = Mock()
        mock_tag = Mock()
        mock_tag.tag = "v1.0.0"
        mock_tag.message = "Release v1.0.0"
        mock_tag.object.sha = "abc123"
        mock_repo.create_git_tag.return_value = mock_tag
        
        mock_ref = Mock()
        mock_ref.ref = "refs/tags/v1.0.0"
        mock_repo.create_git_ref.return_value = mock_ref
        
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "tag": "v1.0.0",
            "message": "Release v1.0.0",
            "object": "abc123"
        })
        
        assert result.success


class TestListWorkflowsToolComprehensive:
    """Comprehensive tests for ListWorkflowsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListWorkflowsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_workflows_success(self, test_username):
        """Test successfully listing workflows."""
        mock_repo = Mock()
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.path = ".github/workflows/ci.yml"
        mock_workflow.state = "active"
        mock_workflow.created_at = create_mock_datetime("2024-01-01")
        mock_workflow.updated_at = create_mock_datetime("2024-01-02")
        mock_repo.get_workflows.return_value = [mock_workflow]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["workflows"]) == 1
        assert result.output["workflows"][0]["name"] == "CI"

    @pytest.mark.asyncio
    async def test_list_workflows_multiple(self, test_username):
        """Test listing multiple workflows."""
        mock_repo = Mock()
        mock_ci = Mock()
        mock_ci.id = 123
        mock_ci.name = "CI"
        mock_ci.path = ".github/workflows/ci.yml"
        mock_ci.state = "active"
        
        mock_deploy = Mock()
        mock_deploy.id = 456
        mock_deploy.name = "Deploy"
        mock_deploy.path = ".github/workflows/deploy.yml"
        mock_deploy.state = "active"
        
        mock_repo.get_workflows.return_value = [mock_ci, mock_deploy]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["workflows"]) == 2


class TestGetWorkflowToolComprehensive:
    """Comprehensive tests for GetWorkflowTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetWorkflowTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_workflow_by_id(self, test_username):
        """Test getting workflow by ID."""
        mock_repo = Mock()
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.path = ".github/workflows/ci.yml"
        mock_workflow.state = "active"
        mock_repo.get_workflow.return_value = mock_workflow
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": 123
        })
        
        assert result.success
        assert result.output["workflow"]["id"] == 123

    @pytest.mark.asyncio
    async def test_get_workflow_by_filename(self, test_username):
        """Test getting workflow by filename."""
        mock_repo = Mock()
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.path = ".github/workflows/ci.yml"
        mock_workflow.state = "active"
        mock_repo.get_workflow.return_value = mock_workflow
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": "ci.yml"
        })
        
        assert result.success


class TestTriggerWorkflowToolComprehensive:
    """Comprehensive tests for TriggerWorkflowTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = TriggerWorkflowTool(self.manager)

    @pytest.mark.asyncio
    async def test_trigger_workflow_success(self, test_username):
        """Test successfully triggering a workflow."""
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.create_dispatch.return_value = True
        mock_repo.get_workflow.return_value = mock_workflow
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": 123
        })
        
        assert result.success
        mock_workflow.create_dispatch.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_workflow_with_ref(self, test_username):
        """Test triggering workflow on specific ref."""
        mock_repo = Mock()
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.create_dispatch.return_value = True
        mock_repo.get_workflow.return_value = mock_workflow
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": 123,
            "ref": "develop"
        })
        
        assert result.success

    @pytest.mark.asyncio
    async def test_trigger_workflow_with_inputs(self, test_username):
        """Test triggering workflow with inputs."""
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_workflow = Mock()
        mock_workflow.id = 123
        mock_workflow.name = "Deploy"
        mock_workflow.create_dispatch.return_value = True
        mock_repo.get_workflow.return_value = mock_workflow
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "workflow_id": 123,
            "inputs": {
                "environment": "production",
                "version": "1.0.0"
            }
        })
        
        assert result.success


class TestListWorkflowRunsToolComprehensive:
    """Comprehensive tests for ListWorkflowRunsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = ListWorkflowRunsTool(self.manager)

    @pytest.mark.asyncio
    async def test_list_workflow_runs_success(self, test_username):
        """Test successfully listing workflow runs."""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 1
        mock_run.name = "CI"
        mock_run.status = "completed"
        mock_run.conclusion = "success"
        mock_run.head_branch = "main"
        mock_run.head_sha = "abc123"
        mock_run.created_at = create_mock_datetime("2024-01-01")
        mock_run.html_url = "https://github.com/{test_username}/repo/actions/runs/1"
        mock_repo.get_workflow_runs.return_value = [mock_run]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({"repository": f"{test_username}/repo"})
        
        assert result.success
        assert len(result.output["runs"]) == 1

    @pytest.mark.asyncio
    async def test_list_workflow_runs_filtered_by_status(self, test_username):
        """Test listing workflow runs filtered by status."""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 1
        mock_run.status = "in_progress"
        mock_run.head_branch = "main"
        mock_run.html_url = "https://github.com/{test_username}/repo/actions/runs/1"
        mock_repo.get_workflow_runs.return_value = [mock_run]
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "status": "in_progress"
        })
        
        assert result.success


class TestGetWorkflowRunToolComprehensive:
    """Comprehensive tests for GetWorkflowRunTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = GetWorkflowRunTool(self.manager)

    @pytest.mark.asyncio
    async def test_get_workflow_run_success(self, test_username):
        """Test successfully getting workflow run."""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 12345
        mock_run.name = "CI"
        mock_run.status = "completed"
        mock_run.conclusion = "success"
        mock_run.workflow_id = 1
        mock_run.run_number = 42
        mock_run.event = "push"
        mock_run.head_branch = "main"
        mock_run.head_sha = "abc123"
        mock_run.created_at = create_mock_datetime("2024-01-01")
        mock_run.updated_at = create_mock_datetime("2024-01-01")
        mock_run.run_started_at = create_mock_datetime("2024-01-01")
        mock_run.actor.login = f"{test_username}"
        mock_run.html_url = "https://github.com/{test_username}/repo/actions/runs/12345"
        mock_run.logs_url = "https://github.com/{test_username}/repo/actions/runs/12345/logs"
        mock_run.cancel_url = "https://github.com/{test_username}/repo/actions/runs/12345/cancel"
        mock_run.rerun_url = "https://github.com/{test_username}/repo/actions/runs/12345/rerun"
        mock_run.jobs.return_value = []
        mock_repo.get_workflow_run.return_value = mock_run
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "run_id": 12345
        })
        
        assert result.success
        assert result.output["run"]["id"] == 12345


class TestCancelWorkflowRunToolComprehensive:
    """Comprehensive tests for CancelWorkflowRunTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = CancelWorkflowRunTool(self.manager)

    @pytest.mark.asyncio
    async def test_cancel_workflow_run_success(self, test_username):
        """Test successfully cancelling a workflow run."""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 12345
        mock_run.cancel.return_value = True
        mock_repo.get_workflow_run.return_value = mock_run
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "run_id": 12345
        })
        
        assert result.success
        mock_run.cancel.assert_called_once()


class TestRerunWorkflowToolComprehensive:
    """Comprehensive tests for RerunWorkflowTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.manager.is_authenticated.return_value = True
        self.tool = RerunWorkflowTool(self.manager)

    @pytest.mark.asyncio
    async def test_rerun_workflow_success(self, test_username):
        """Test successfully rerunning a workflow."""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 12345
        mock_run.status = "completed"
        mock_run.rerun.return_value = True
        mock_repo.get_workflow_run.return_value = mock_run
        self.manager.get_repository.return_value = mock_repo

        result = await self.tool.execute({
            "repository": f"{test_username}/repo",
            "run_id": 12345
        })
        
        assert result.success
        mock_run.rerun.assert_called_once()
