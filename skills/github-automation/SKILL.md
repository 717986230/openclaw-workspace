---
name: github-automation
description: An automated Pull Request system for discovering projects, analyzing issues, and creating PRs.
version: 1.0.0
author: Erbing
triggers:
  - "auto pr"
  - "github automation"
  - "create pr"
  - "analyze issues"
  - "discover projects"
  - "自动PR"
  - "GitHub自动化"
  - "发现项目"
dependencies:
  tools:
    - read
    - write
    - exec
  libraries:
    - subprocess
    - json
    - requests
    - pathlib
    - datetime
    - typing
    - argparse
capabilities:
  - project_discovery
  - issue_analysis
  - pr_creation
  - progress_tracking
  - repo_stats
  - dry_run_mode
  - caching
  - intelligent_filtering
---

# GitHub Automation Skill

This skill provides an automated Pull Request system for Erbing, enabling the discovery of projects, analysis of issues, and creation of PRs. It uses data-driven project selection and intelligent issue filtering.

## How It Works

1. **Project Discovery:** Dynamically discovers popular projects based on stars, activity, and "good first issue" count.
2. **Issue Analysis:** Analyzes issues to determine if they are fixable and prioritizes them.
3. **PR Creation:** Automatically creates PRs for fixable issues.
4. **Progress Tracking:** Tracks processed issues and PR status.
5. **Repo Stats:** Provides statistics on repository health and activity.

## Usage

### Basic Operations

**Run the Workflow:**
```python
workflow = AutoPRWorkflow(dry_run=False)
workflow.run(limit=3, project_limit=5)
```

**Check PR Status:**
```python
workflow.check_prs()
```

### Advanced Operations

**Get Recommended Projects:**
```python
projects = selector.get_recommended_projects(limit=10)
```

**Search for Issues:**
```python
issues = workflow.search_issues(projects, limit=5)
```

**Process a Single Issue:**
```python
result = workflow.process_issue(issue)
```

## Examples

### Example 1: Discovering Projects

**User:** "Find good projects to contribute to."

**Agent:** [Analyzes projects and recommends top candidates based on stars, activity, and GFI count]

### Example 2: Analyzing Issues

**User:** "Analyze issues in the `pallets/flask` repository."

**Agent:** [Searches for issues, filters out simple docs, and prioritizes fixable bugs]

### Example 3: Creating PRs

**User:** "Create PRs for the top 3 issues."

**Agent:** [Processes issues, creates forks, and opens PRs with appropriate descriptions]

### Example 4: Dry Run Mode

**User:** "Test the automation without making real changes."

**Agent:** [Runs workflow with `--dry-run` flag, simulating all operations]

## Key Features

- **Data-Driven Selection:** Uses metrics to select the best projects.
- **Intelligent Filtering:** Excludes simple documentation issues automatically.
- **Progress Tracking:** Keeps track of processed issues and PR status.
- **Dry Run Mode:** Allows testing without making actual changes.
- **Caching:** Caches project data to improve performance.
- **Fork Management:** Automatically handles forking and branch creation.

## Dependencies

### Required Libraries
- `subprocess` - Process execution for git and gh commands
- `json` - Data handling for API responses
- `requests` - HTTP requests to GitHub API
- `pathlib` - Path operations for file management
- `datetime` - Time handling for progress tracking
- `typing` - Type hints for code quality
- `argparse` - CLI argument parsing

### External Tools
- **GitHub CLI (`gh`)** - Required for authentication and API calls
  - Must be authenticated (`gh auth login`)
  - Requires `repo` and `workflow` scopes
  - Version 2.0.0 or higher recommended

### API Requirements
- GitHub Personal Access Token (handled via `gh` CLI)
- Rate limits: 5000 requests/hour (authenticated)
- Unauthenticated: 60 requests/hour (not recommended)

## Configuration

### Environment Variables
- `GITHUB_TOKEN` - Optional, can use `gh` auth instead
- `AUTO_PR_DRY_RUN` - Set to "true" for default dry run mode
- `AUTO_PR_CACHE_DIR` - Custom cache directory (default: `.cache`)

### Progress File
- Location: `progress.json` in working directory
- Tracks: processed issues, PR URLs, timestamps
- Auto-created on first run

## Best Practices

- **Use Dry Run:** Test the workflow with `--dry-run` before making actual changes.
- **Monitor Progress:** Check the progress file to see what has been processed.
- **Filter Issues:** Use the issue analyzer to avoid simple documentation tasks.
- **Check PR Status:** Regularly check the status of created PRs.
- **Respect Rate Limits:** Use caching to minimize API calls.

## Troubleshooting

### Common Issues

1. **"gh: command not found" error:**
   - Install GitHub CLI: `brew install gh` (macOS) or `choco install gh` (Windows)
   - Ensure `gh` is in your PATH

2. **"Authentication required" error:**
   - Run `gh auth login` and follow the prompts
   - Ensure you have `repo` scope permissions

3. **Rate limit exceeded:**
   - Wait for rate limit reset (1 hour window)
   - Use authenticated mode for higher limits
   - Enable caching to reduce API calls

4. **"Fork already exists" error:**
   - Delete existing fork or use `--force` flag
   - Check fork status in progress file

5. **PR creation fails:**
   - Verify branch exists in fork
   - Check for merge conflicts
   - Ensure upstream repository allows PRs from forks

## Contributing

To extend this skill:
1. Add new analysis methods to the `IssueAnalyzer` class.
2. Update the `SKILL.md` with new capabilities.
3. Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
