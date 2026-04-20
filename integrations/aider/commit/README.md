# Aider Automated Commit Integration

## Overview

This module provides intelligent commit automation for the Aider framework. It generates semantic commit messages, groups related changes, and ensures atomic commits following best practices.

## Features

### Smart Commit Messages

- AI-generated commit messages
- Conventional Commits format
- Change categorization
- Scope detection
- Breaking change handling

### Atomic Commits

- Group related changes
- Split large changes logically
- Ensure single-purpose commits
- Maintain commit coherence

### Commit Workflow

- Staged changes analysis
- Pre-commit validation
- Post-commit hooks
- Commit history management

## Quick Start

### Basic Commit

```python
from openclaw.integrations.aider.commit import CommitManager

# Initialize
commit = CommitManager(repo_path="/path/to/repo")

# Smart commit with auto-generated message
result = commit.smart_commit()

print(f"Committed: {result.hash}")
print(f"Message: {result.message}")
```

### Categorized Commit

```python
# Specify commit type
result = commit.commit(
    type="feat",
    scope="auth",
    breaking=False,
    description="Add user authentication"
)
```

### Atomic Commits

```python
# Analyze staged changes
analysis = commit.analyze_staged()

# Group into atomic commits
groups = commit.group_changes(analysis)

# Create multiple commits
for group in groups:
    result = commit.commit_group(group)
    print(f"Created commit: {result.hash}")
```

## Conventional Commits

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |
| `perf` | Performance improvements |
| `ci` | CI/CD changes |
| `build` | Build system changes |

### Examples

```
feat(auth): add OAuth2 authentication

Implement OAuth2 login flow with Google and GitHub providers.
Includes token refresh handling and session management.

Closes #123
```

```
fix(api): resolve timeout issue in user endpoint

The API was timing out on large user queries. Added pagination
to handle large result sets efficiently.

Fixes #456
```

## API Reference

### CommitManager

```python
class CommitManager:
    """Manage automated commits."""
    
    def __init__(
        self,
        repo_path: str = ".",
        config: CommitConfig = None
    ):
        """Initialize commit manager."""
        
    def smart_commit(
        self,
        auto_stage: bool = False
    ) -> CommitResult:
        """
        Create commit with AI-generated message.
        
        Args:
            auto_stage: Automatically stage all changes
            
        Returns:
            CommitResult with commit details
        """
        
    def commit(
        self,
        type: str = None,
        scope: str = None,
        description: str = None,
        body: str = None,
        breaking: bool = False,
        footer: List[str] = None
    ) -> CommitResult:
        """Create commit with specified parameters."""
        
    def analyze_staged(self) -> ChangeAnalysis:
        """Analyze staged changes."""
        
    def analyze_changes(
        self,
        files: List[str] = None
    ) -> ChangeAnalysis:
        """Analyze file changes."""
        
    def group_changes(
        self,
        analysis: ChangeAnalysis
    ) -> List[ChangeGroup]:
        """Group changes into atomic commits."""
        
    def commit_group(
        self,
        group: ChangeGroup
    ) -> CommitResult:
        """Commit a group of changes."""
        
    def generate_message(
        self,
        analysis: ChangeAnalysis
    ) -> str:
        """Generate commit message from analysis."""
```

### ChangeAnalysis

```python
@dataclass
class ChangeAnalysis:
    """Analysis of code changes."""
    
    files: List[ChangedFile]
    categories: Dict[str, List[str]]
    scope: str
    type: str
    description: str
    breaking_changes: List[str]
    related_issues: List[str]
    
    def get_primary_type(self) -> str:
        """Get primary change type."""
        
    def get_primary_scope(self) -> str:
        """Get primary scope."""
        
    def generate_summary(self) -> str:
        """Generate change summary."""
```

### CommitResult

```python
@dataclass
class CommitResult:
    """Result of commit operation."""
    
    success: bool
    hash: str
    message: str
    files: List[str]
    stats: CommitStats
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
```

## Configuration

### Commit Config

```yaml
aider:
  commit:
    enabled: true
    
    # Message format
    format: conventional  # conventional, simple, custom
    max_subject_length: 72
    max_body_width: 100
    
    # Behavior
    auto_stage: false
    auto_push: false
    sign_commits: false
    
    # Atomic commits
    atomic:
      enabled: true
      max_files: 10
      group_by: ["directory", "type", "feature"]
    
    # Templates
    templates:
      conventional: "{type}({scope}): {description}"
      simple: "{description}"
      custom: "[{type}] {scope}: {description}"
    
    # Hooks
    pre_commit:
      - lint
      - test
      - review
    
    post_commit:
      - notify
      - update-changelog
```

### Type Detection Rules

```yaml
aider:
  commit:
    type_detection:
      - pattern: "^src/features/"
        type: feat
      - pattern: "^src/fixes/"
        type: fix
      - pattern: "^docs/"
        type: docs
      - pattern: "^tests/"
        type: test
      - pattern: "\.md$"
        type: docs
      - pattern: "\.test\."
        type: test
```

## Examples

### Feature Commit

```python
commit = CommitManager()

# Add feature files
# ... edit files ...

# Stage changes
commit.stage(["src/features/user-auth.py"])

# Analyze
analysis = commit.analyze_staged()

# Generate message
message = commit.generate_message(analysis)
# Output: "feat(auth): implement user authentication"

# Commit
result = commit.commit()
```

### Bug Fix Commit

```python
commit = CommitManager()

# Fix bug
# ... edit files ...

# Smart commit
result = commit.smart_commit()
# AI generates: "fix(api): resolve timeout on large queries"
```

### Breaking Change Commit

```python
commit = CommitManager()

# Make breaking change
# ... edit files ...

# Commit with breaking change marker
result = commit.commit(
    type="refactor",
    scope="api",
    breaking=True,
    description="change API response format"
)
# Message: "refactor(api)!: change API response format"
```

### Atomic Commits

```python
commit = CommitManager()

# Multiple related changes
# ... edit many files ...

# Stage all
commit.stage(all=True)

# Analyze
analysis = commit.analyze_staged()

# Group into atomic commits
groups = commit.group_changes(analysis)

# Create commits
for group in groups:
    result = commit.commit_group(group)
    print(f"Commit: {result.message}")
```

## Commit Message Generation

### AI-Powered Generation

```python
class MessageGenerator:
    """Generate commit messages using AI."""
    
    def generate(
        self,
        analysis: ChangeAnalysis
    ) -> str:
        """
        Generate commit message from analysis.
        
        Process:
        1. Analyze changed files and diff
        2. Categorize changes
        3. Determine scope and type
        4. Generate description
        5. Format according to conventions
        """
        
    def categorize(self, analysis: ChangeAnalysis) -> str:
        """Determine commit type."""
        # Check patterns
        if self.has_new_features(analysis):
            return "feat"
        elif self.has_bug_fixes(analysis):
            return "fix"
        elif self.has_refactoring(analysis):
            return "refactor"
        # ... more patterns
        
    def extract_scope(self, analysis: ChangeAnalysis) -> str:
        """Extract scope from changes."""
        # Analyze file paths
        # Find common directory or module
        # Return scope
        
    def generate_description(
        self,
        analysis: ChangeAnalysis
    ) -> str:
        """Generate commit description."""
        # Use AI to summarize changes
        # Make description imperative
        # Keep under max length
```

### Message Templates

```python
# Conventional Commits template
CONVENTIONAL_TEMPLATE = """
{type}{scope}: {description}

{body}

{footer}
"""

# Simple template
SIMPLE_TEMPLATE = """
{description}

{body}
"""

# Custom template
CUSTOM_TEMPLATE = """
[{type}] {scope}: {description}

Changes:
{changes}

{footer}
"""
```

## Commit Hooks

### Pre-commit Hook

```python
def pre_commit_hook():
    """Run before commit."""
    commit = CommitManager()
    
    # Get staged changes
    analysis = commit.analyze_staged()
    
    # Run checks
    checks = [
        LintCheck(),
        FormatCheck(),
        TestCheck(),
    ]
    
    for check in checks:
        result = check.run(analysis)
        if not result.passed:
            print(f"Check failed: {check.name}")
            print(result.message)
            return False
    
    return True
```

### Post-commit Hook

```python
def post_commit_hook(commit_hash: str):
    """Run after commit."""
    commit = CommitManager()
    
    # Get commit info
    info = commit.get_commit(commit_hash)
    
    # Update changelog
    if info.type in ['feat', 'fix']:
        update_changelog(info)
    
    # Notify team
    if info.breaking:
        notify_breaking_change(info)
    
    # Update issue
    if info.related_issues:
        update_issues(info)
```

## Changelog Integration

### Auto-generate Changelog

```python
def update_changelog(commit: CommitInfo):
    """Update CHANGELOG.md."""
    changelog = ChangelogManager()
    
    # Read existing changelog
    entries = changelog.read()
    
    # Add new entry
    entry = ChangelogEntry(
        type=commit.type,
        scope=commit.scope,
        description=commit.description,
        hash=commit.hash,
        date=commit.date
    )
    
    entries.append(entry)
    
    # Write changelog
    changelog.write(entries)
```

### Changelog Format

```markdown
# Changelog

## [Unreleased]

### Features
- **auth**: Add user authentication (#abc123)

### Bug Fixes
- **api**: Resolve timeout on large queries (#def456)

## [1.0.0] - 2026-04-16
...
```

## Best Practices

1. **Atomic Commits:** One logical change per commit
2. **Clear Messages:** Describe what and why, not how
3. **Consistent Format:** Follow chosen convention
4. **Reference Issues:** Link to related issues
5. **Test Before Commit:** Run tests on staged changes
6. **Review Before Push:** Verify commit history

## Troubleshooting

### Empty Commit

```python
# Force empty commit
commit.commit(allow_empty=True)
```

### Amend Last Commit

```python
# Amend previous commit
commit.amend(message="Updated message")
```

### Split Commit

```python
# Reset to previous commit
commit.reset_soft("HEAD~1")

# Stage and commit separately
commit.stage(["file1.py"])
commit.commit()

commit.stage(["file2.py"])
commit.commit()
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-16
