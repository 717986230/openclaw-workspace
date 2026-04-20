# Aider Git Integration

## Overview

This module provides Git integration capabilities for the Aider framework within OpenClaw. It enables AI-assisted Git operations, branch management, and intelligent merge conflict resolution.

## Features

### Repository Management

- Initialize repositories with OpenClaw conventions
- Configure Git settings automatically
- Set up hooks and templates
- Manage remote repositories

### Branch Operations

- Create feature/fix/refactor branches
- Smart branch naming conventions
- Branch protection enforcement
- Branch cleanup automation

### Merge Operations

- AI-assisted conflict resolution
- Safe merge strategies
- Rebase workflows
- Cherry-pick support

### Change Tracking

- Intelligent diff analysis
- Change categorization
- Impact assessment
- Related files detection

## Quick Start

### Initialize Git Integration

```python
from openclaw.integrations.aider.git import GitManager

# Initialize
git = GitManager(repo_path="/path/to/repo")

# Check status
status = git.status()
print(status)
```

### Branch Management

```python
# Create feature branch
git.create_branch("feature/user-auth", base="main")

# List branches
branches = git.list_branches()

# Switch branch
git.switch_branch("feature/user-auth")

# Delete branch
git.delete_branch("feature/user-auth")
```

### Merge Operations

```python
# Merge branch
result = git.merge("feature/user-auth", target="main")

# Check for conflicts
if result.has_conflicts:
    conflicts = git.get_conflicts()
    resolutions = git.ai_resolve_conflicts(conflicts)
    git.apply_resolutions(resolutions)

# Complete merge
git.commit_merge()
```

## API Reference

### GitManager

```python
class GitManager:
    def __init__(self, repo_path: str = "."):
        """Initialize Git manager for repository."""
        
    def status(self) -> GitStatus:
        """Get repository status."""
        
    def create_branch(self, name: str, base: str = "HEAD") -> Branch:
        """Create new branch from base."""
        
    def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete branch."""
        
    def switch_branch(self, name: str) -> None:
        """Switch to branch."""
        
    def merge(self, source: str, target: str = "HEAD") -> MergeResult:
        """Merge source into target."""
        
    def diff(self, ref1: str = None, ref2: str = None) -> DiffResult:
        """Get diff between refs."""
        
    def ai_resolve_conflicts(self, conflicts: List[Conflict]) -> List[Resolution]:
        """Use AI to resolve merge conflicts."""
```

### GitStatus

```python
@dataclass
class GitStatus:
    branch: str
    staged: List[str]
    unstaged: List[str]
    untracked: List[str]
    ahead: int
    behind: int
    conflicts: List[str]
```

### MergeResult

```python
@dataclass
class MergeResult:
    success: bool
    has_conflicts: bool
    conflicts: List[Conflict]
    fast_forward: bool
    merged_branches: List[str]
```

## Configuration

### Branch Naming Conventions

```yaml
aider:
  git:
    branch_prefixes:
      feature: "feature/"
      fix: "fix/"
      refactor: "refactor/"
      docs: "docs/"
      test: "test/"
      
    branch_template: "{prefix}{ticket}-{description}"
    
    protected_branches:
      - main
      - master
      - develop
      - release/*
```

### Merge Strategies

```yaml
aider:
  git:
    merge_strategy: "recursive"  # recursive, ours, theirs, octopus
    conflict_resolution: "ai"    # ai, manual, ours, theirs
    auto_resolve_simple: true
```

## Examples

### Feature Development Workflow

```python
# 1. Create feature branch
git.create_branch("feature/user-auth")

# 2. Make changes with Aider
# ... editing files ...

# 3. Check changes
diff = git.diff()
print(f"Changed files: {diff.files}")

# 4. Commit changes
git.add(all=True)
git.commit("feat(auth): implement user authentication")

# 5. Push branch
git.push("origin", "feature/user-auth")

# 6. Create pull request
pr = git.create_pr(
    title="Implement user authentication",
    body="Added login/logout functionality"
)
```

### Conflict Resolution

```python
# Attempt merge
result = git.merge("feature/user-auth")

if result.has_conflicts:
    # Get conflict details
    for conflict in result.conflicts:
        print(f"Conflict in {conflict.file}")
        print(f"  Ours: {conflict.ours}")
        print(f"  Theirs: {conflict.theirs}")
    
    # AI resolution
    resolutions = git.ai_resolve_conflicts(result.conflicts)
    
    # Apply resolutions
    for resolution in resolutions:
        git.apply_resolution(resolution)
    
    # Complete merge
    git.commit_merge("Merge feature/user-auth")
```

### Branch Cleanup

```python
# List all branches
branches = git.list_branches()

# Find merged branches
merged = [b for b in branches if b.merged]

# Delete merged local branches
for branch in merged:
    if not branch.protected:
        git.delete_branch(branch.name)

# Prune remote branches
git.fetch(prune=True)
```

## Best Practices

1. **Use Feature Branches:** Always create branches for new work
2. **Keep Branches Updated:** Regularly rebase on main
3. **Resolve Conflicts Early:** Address conflicts promptly
4. **Atomic Commits:** Make focused, single-purpose commits
5. **Test Before Merge:** Run tests before merging
6. **Clean Up:** Delete merged branches

## Troubleshooting

### Detached HEAD State

```python
# Check current state
if git.is_detached():
    # Create branch from current commit
    git.create_branch("recovery-branch")
    git.switch_branch("recovery-branch")
```

### Uncommitted Changes During Merge

```python
# Stash changes
git.stash("pre-merge-stash")

# Perform merge
result = git.merge("feature/branch")

# Restore stash
git.stash_pop()
```

### Force Push Protection

```python
# Check branch protection
if git.is_protected("main"):
    print("Cannot force push to main")
else:
    git.push(force=True)
```

## Related Documentation

- [Git Operations Detail](git-operations.md)
- [Review Workflow](../review/README.md)
- [Commit Workflow](../commit/README.md)

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-16
