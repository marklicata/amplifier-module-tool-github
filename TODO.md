# Future Features & TODO

This document tracks features planned for future versions of the GitHub module.

## Version 1.0 (Current - Issues Only)

**Status:** ✅ Complete

- [x] List issues with filtering
- [x] Get issue details with comments
- [x] Create new issues
- [x] Update existing issues
- [x] Add comments to issues
- [x] Error handling and authentication
- [x] Rate limit handling
- [x] Basic test suite

## Version 1.1 - Pull Requests (Planned)

**Priority:** High

### Tools to Implement:
- [ ] `github_list_pull_requests` - List PRs with filtering
  - Filter by state, author, reviewer, labels
  - Sort options
  - Include draft PRs
  
- [ ] `github_get_pull_request` - Get PR details
  - Include files changed
  - Include review comments
  - Include status checks
  
- [ ] `github_create_pull_request` - Create new PR
  - Set title, body, base, head
  - Set reviewers, labels
  - Mark as draft
  
- [ ] `github_update_pull_request` - Update PR
  - Update title, body
  - Change state (open/closed)
  - Update reviewers, labels
  
- [ ] `github_merge_pull_request` - Merge PR
  - Merge strategies (merge, squash, rebase)
  - Delete branch option
  
- [ ] `github_review_pull_request` - Review PR
  - Approve, request changes, comment
  - Add review comments

### Files to Create:
- `tools/pull_requests/list.py`
- `tools/pull_requests/get.py`
- `tools/pull_requests/create.py`
- `tools/pull_requests/update.py`
- `tools/pull_requests/merge.py`
- `tools/pull_requests/review.py`

## Version 1.2 - Repositories (Planned)

**Priority:** Medium

### Tools to Implement:
- [ ] `github_get_repository` - Get repo details
  - Basic info, stats, settings
  
- [ ] `github_list_repositories` - List repos
  - For user or organization
  - Filter by type, language
  
- [ ] `github_create_repository` - Create new repo
  - Public/private
  - Initialize with README, .gitignore
  
- [ ] `github_get_file_content` - Get file from repo
  - Support different refs (branches, tags)
  
- [ ] `github_list_repository_contents` - List directory contents
  - Recursive option

### Files to Create:
- `tools/repositories/get.py`
- `tools/repositories/list.py`
- `tools/repositories/create.py`
- `tools/repositories/get_file_content.py`
- `tools/repositories/list_contents.py`

## Version 1.3 - Commits & Branches (Planned)

**Priority:** Medium

### Tools to Implement:

#### Commits:
- [ ] `github_list_commits` - List commits
  - Filter by author, path, date range
  
- [ ] `github_get_commit` - Get commit details
  - Files changed
  - Commit message, stats

#### Branches:
- [ ] `github_list_branches` - List branches
  - Include protection status
  
- [ ] `github_get_branch` - Get branch details
  - Protection rules
  - Latest commit
  
- [ ] `github_create_branch` - Create new branch
  - From specific ref
  
- [ ] `github_compare_branches` - Compare two branches
  - Files changed
  - Commit diff

### Files to Create:
- `tools/commits/list.py`
- `tools/commits/get.py`
- `tools/branches/list.py`
- `tools/branches/get.py`
- `tools/branches/create.py`
- `tools/branches/compare.py`

## Version 1.4 - Releases & Tags (Planned)

**Priority:** Low

### Tools to Implement:
- [ ] `github_list_releases` - List releases
  - Include draft and pre-releases
  
- [ ] `github_get_release` - Get release details
  - Assets, download counts
  
- [ ] `github_create_release` - Create new release
  - Upload assets
  - Set as draft or pre-release
  
- [ ] `github_list_tags` - List tags
  
- [ ] `github_create_tag` - Create new tag

### Files to Create:
- `tools/releases/list.py`
- `tools/releases/get.py`
- `tools/releases/create.py`
- `tools/releases/list_tags.py`
- `tools/releases/create_tag.py`

## Version 1.5 - Actions & Workflows (Planned)

**Priority:** High

### Tools to Implement:
- [ ] `github_list_workflows` - List workflows
  
- [ ] `github_get_workflow` - Get workflow details
  
- [ ] `github_trigger_workflow` - Manually trigger workflow
  - Pass inputs
  
- [ ] `github_list_workflow_runs` - List workflow runs
  - Filter by status, conclusion
  
- [ ] `github_get_workflow_run` - Get run details
  - Jobs, steps, logs
  
- [ ] `github_cancel_workflow_run` - Cancel running workflow
  
- [ ] `github_rerun_workflow` - Rerun failed workflow

### Files to Create:
- `tools/actions/list_workflows.py`
- `tools/actions/get_workflow.py`
- `tools/actions/trigger_workflow.py`
- `tools/actions/list_runs.py`
- `tools/actions/get_run.py`
- `tools/actions/cancel_run.py`
- `tools/actions/rerun.py`

## Version 2.0 - Projects & Advanced Features (Future)

**Priority:** Low

### GitHub Projects:
- [ ] List projects
- [ ] Get project details
- [ ] Create/update projects
- [ ] Manage project items

### Code Search:
- [ ] `github_search_code` - Search code across repos
- [ ] `github_search_repositories` - Search repositories
- [ ] `github_search_users` - Search users

### Security:
- [ ] `github_list_dependabot_alerts` - List Dependabot alerts
- [ ] `github_get_security_advisories` - Get security advisories
- [ ] `github_list_secret_scanning_alerts` - List secret scanning alerts

### Advanced Repository:
- [ ] Webhooks management
- [ ] Deploy keys management
- [ ] Collaborators management
- [ ] Branch protection rules

### Discussions:
- [ ] List/create/update discussions
- [ ] Discussion comments

## Implementation Guidelines

When implementing new tools:

1. **Follow the pattern**: Use `GitHubBaseTool` as base class
2. **Error handling**: Use exception classes from `exceptions.py`
3. **Documentation**: Update README.md with tool descriptions
4. **Tests**: Add test cases to `tests/test_tools.py`
5. **Input validation**: Use JSON schema for input validation
6. **Output format**: Return structured data with ToolResult
7. **Rate limiting**: Handle rate limit exceptions
8. **Authentication**: Check authentication before operations

## Dependencies to Consider

For future versions, we may need:

- **GraphQL support**: For more efficient queries (consider `gql` library)
- **Async support**: Full async/await for PyGithub operations
- **Caching**: Cache frequently accessed data (consider `cachetools`)
- **Webhooks**: Listen to GitHub events (consider `flask` or `fastapi`)

## Performance Optimizations

- Implement pagination helpers
- Add response caching for read-only operations
- Batch operations where possible
- Use conditional requests (ETags)
- Implement rate limit tracking and backoff

## Documentation Improvements

- Add more code examples
- Create API reference documentation
- Add troubleshooting guide
- Create migration guide for breaking changes
- Add architecture decision records (ADRs)
