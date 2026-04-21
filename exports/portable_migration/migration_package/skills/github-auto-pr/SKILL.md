# github-auto-pr Skill

## Description
Automatically scan trending GitHub repositories, detect issues, and create pull requests.

## Features
- **Multi-language Support**: Python, JavaScript, TypeScript, Go, Rust
- **Issue Detection Types**:
  - Typos in documentation
  - Missing CONTRIBUTING.md
  - Missing SECURITY.md
  - Good first issues
  - Security vulnerabilities (via Dependabot)
  - Code quality issues
- **Smart Priority**: Security > Bug > Typo > Documentation
- **Auto Learning**: Saves results to database for continuous improvement

## Usage

### Run Once
```bash
python scripts/github_trending_auto_pr.py --run
```

### Run Hourly (Scheduled)
```bash
python scripts/github_trending_auto_pr.py --schedule
```

### Scan Specific Language
```bash
python scripts/github_trending_auto_pr.py --language python --limit 20
```

## Configuration

Edit the script to modify:
- `MAX_PROJECTS`: Number of projects to scan (default: 20)
- `MAX_PRS_PER_RUN`: Maximum PRs per run (default: 3)
- `LANGUAGES`: Languages to scan
- `EXCLUDE_REPOS`: Repositories to skip

## Database Integration

All PRs are logged to SQLite database:
- Path: `memory/database/xiaozhi_memory.db`
- Type: `event`
- Category: `github`

## Output

### Console
```
=== Discovering trending python repos ===
Found 20 repos

=== Analyzing donnemartin/system-design-primer ===
Stars: 340,000 | Issues: 246
Found 3 potential issues

--- Creating PR: typo for owner/repo ---
PR created: https://github.com/owner/repo/pull/123

=== Completed: 3 PRs created ===
```

### Database
```json
{
  "type": "event",
  "title": "PR Created: owner/repo",
  "content": "Type: typo\nURL: https://github.com/owner/repo/pull/123",
  "category": "github",
  "tags": ["pr", "auto"],
  "importance": 8
}
```

## Scheduled Task Setup

### Windows Task Scheduler
```powershell
# Create hourly task
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/github_trending_auto_pr.py --run"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "GitHub-Auto-PR" -Action $action -Trigger $trigger
```

### Cron (Linux/Mac)
```bash
# Run every hour
0 * * * * cd /path/to/workspace && python scripts/github_trending_auto_pr.py --run >> logs/auto-pr.log 2>&1
```

## Learning & Optimization

The skill learns from each run:
1. Records successful PR patterns
2. Tracks which issue types get merged
3. Adjusts priority based on merge rate
4. Excludes repos with maintenance issues

## Prerequisites

1. GitHub CLI authenticated: `gh auth login`
2. Git configured: `git config --global user.email "you@example.com"`
3. Python 3.10+
4. SQLite database initialized

## Troubleshooting

### No PRs Created
- Check GitHub auth: `gh auth status`
- Check rate limits: `gh api rate_limit`
- Verify repository is not in EXCLUDE_REPOS

### Network Errors
- Increase timeout in requests
- Use SSH instead of HTTPS
- Check firewall settings

### Push Failures
- Verify fork permissions
- Check branch conflicts
- Rebase on upstream

## Future Enhancements

- [ ] AI-assisted bug fixing (Claude Code integration)
- [ ] Semantic code analysis
- [ ] Multi-file PR support
- [ ] PR review automation
- [ ] Merge conflict resolution

## Version History

- v1.0.0 (2026-04-03): Initial release
  - Basic issue detection
  - Typo fixing
  - Missing file creation
  - Database logging

---

*This skill is designed to run autonomously and improve over time through learning.*
