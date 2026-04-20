# Git Operations - Detailed Implementation

## Architecture

The Git operations module provides a comprehensive interface for managing Git repositories with AI assistance through Aider.

### Module Structure

```
git/
├── __init__.py
├── manager.py          # GitManager implementation
├── operations.py       # Core Git operations
├── branch.py           # Branch management
├── merge.py            # Merge and conflict resolution
├── diff.py             # Diff analysis
├── hooks.py            # Git hooks management
└── utils.py            # Utility functions
```

## Core Operations

### Repository Initialization

```python
class GitInitializer:
    """Initialize Git repository with OpenClaw conventions."""
    
    def init_repo(self, path: str, config: RepoConfig) -> Repo:
        """
        Initialize new Git repository.
        
        Args:
            path: Repository path
            config: Repository configuration
            
        Returns:
            Initialized repository
        """
        # 1. Create .git directory
        # 2. Configure Git settings
        # 3. Set up hooks
        # 4. Create initial commit
        # 5. Configure remotes
        
    def configure_hooks(self, hooks: List[Hook]) -> None:
        """Set up Git hooks for the repository."""
        
    def create_gitignore(self, template: str) -> None:
        """Create .gitignore from template."""
```

### Status Tracking

```python
class GitStatusTracker:
    """Track repository status in real-time."""
    
    def get_status(self) -> DetailedStatus:
        """
        Get comprehensive repository status.
        
        Returns:
            DetailedStatus with:
            - Current branch
            - Staged files
            - Unstaged modifications
            - Untracked files
            - Stash entries
            - Remote tracking info
            - Merge/rebase state
        """
        
    def watch_changes(self, callback: Callable) -> Watcher:
        """Watch for repository changes."""
        
    def get_file_status(self, path: str) -> FileStatus:
        """Get status of specific file."""
```

### Branch Operations

```python
class BranchManager:
    """Manage Git branches with safety checks."""
    
    def create_branch(
        self,
        name: str,
        base: str = "HEAD",
        track_remote: bool = True
    ) -> Branch:
        """
        Create new branch.
        
        Features:
        - Validates branch name
        - Checks for existing branches
        - Sets up remote tracking
        - Protects reserved names
        """
        
    def list_branches(
        self,
        pattern: str = None,
        remote: bool = False,
        merged: bool = None
    ) -> List[Branch]:
        """List branches with filtering."""
        
    def delete_branch(
        self,
        name: str,
        force: bool = False,
        delete_remote: bool = False
    ) -> None:
        """Delete branch with safety checks."""
        
    def rename_branch(
        self,
        old_name: str,
        new_name: str
    ) -> None:
        """Rename branch."""
```

### Merge Operations

```python
class MergeManager:
    """Handle merge operations with AI assistance."""
    
    def merge(
        self,
        source: str,
        target: str = "HEAD",
        strategy: MergeStrategy = MergeStrategy.RECURSIVE,
        squash: bool = False
    ) -> MergeResult:
        """
        Perform merge operation.
        
        Args:
            source: Source branch/commit
            target: Target branch (default: HEAD)
            strategy: Merge strategy
            squash: Squash commits
            
        Returns:
            MergeResult with status and conflicts
        """
        
    def rebase(
        self,
        source: str,
        target: str = "HEAD",
        interactive: bool = False
    ) -> RebaseResult:
        """Perform rebase operation."""
        
    def cherry_pick(
        self,
        commits: List[str],
        mainline: int = None
    ) -> CherryPickResult:
        """Cherry-pick commits."""
        
    def abort(self) -> None:
        """Abort ongoing merge/rebase."""
```

### Conflict Resolution

```python
class ConflictResolver:
    """AI-assisted conflict resolution."""
    
    def detect_conflicts(self) -> List[Conflict]:
        """
        Detect merge conflicts in repository.
        
        Returns:
            List of Conflict objects with:
            - File path
            - Conflict markers
            - Ours/Theirs sections
            - Context
        """
        
    def analyze_conflict(self, conflict: Conflict) -> ConflictAnalysis:
        """
        Analyze conflict for resolution strategy.
        
        Analysis includes:
        - Type of conflict (content, rename, delete)
        - Semantic analysis
        - Suggested resolution
        - Risk assessment
        """
        
    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: ResolutionStrategy = ResolutionStrategy.AI
    ) -> Resolution:
        """
        Resolve conflict using specified strategy.
        
        Strategies:
        - AI: Use Aider to intelligently merge
        - OURS: Keep our version
        - THEIRS: Keep their version
        - MANUAL: Mark for manual resolution
        """
        
    def apply_resolution(self, resolution: Resolution) -> None:
        """Apply resolution to working directory."""
```

## Diff Analysis

### Change Detection

```python
class DiffAnalyzer:
    """Analyze changes between Git references."""
    
    def diff(
        self,
        ref1: str = None,
        ref2: str = None,
        paths: List[str] = None
    ) -> DiffResult:
        """
        Get diff between references.
        
        Args:
            ref1: First reference (default: index)
            ref2: Second reference (default: working tree)
            paths: Limit to specific paths
            
        Returns:
            DiffResult with:
            - Changed files
            - Statistics
            - Patch content
        """
        
    def diff_stats(self, diff: DiffResult) -> DiffStats:
        """Calculate diff statistics."""
        
    def classify_changes(self, diff: DiffResult) -> ChangeClassification:
        """
        Classify changes by type.
        
        Categories:
        - Feature additions
        - Bug fixes
        - Refactoring
        - Documentation
        - Tests
        - Configuration
        """
```

### Change Impact

```python
class ImpactAnalyzer:
    """Analyze impact of changes."""
    
    def analyze_impact(self, diff: DiffResult) -> ImpactReport:
        """
        Analyze potential impact of changes.
        
        Analysis includes:
        - Affected components
        - Breaking changes
        - Dependencies
        - Test coverage needed
        """
        
    def find_related_files(self, file: str) -> List[str]:
        """Find files related to changed file."""
        
    def suggest_tests(self, changes: List[str]) -> List[str]:
        """Suggest tests to run for changes."""
```

## Git Hooks

### Hook Management

```python
class HookManager:
    """Manage Git hooks."""
    
    def install_hook(
        self,
        hook_type: HookType,
        script: str,
        enforce: bool = True
    ) -> None:
        """
        Install Git hook.
        
        Hook types:
        - PRE_COMMIT
        - PRE_PUSH
        - POST_COMMIT
        - POST_MERGE
        - PRE_REBASE
        """
        
    def remove_hook(self, hook_type: HookType) -> None:
        """Remove Git hook."""
        
    def run_hook(self, hook_type: HookType, args: List[str]) -> HookResult:
        """Run hook manually."""
```

### Pre-commit Hook

```python
def pre_commit_hook():
    """
    Pre-commit hook implementation.
    
    Checks:
    1. Code formatting (Prettier, Black)
    2. Linting (ESLint, Pylint)
    3. Type checking
    4. Tests pass
    5. No secrets in code
    6. Commit message format
    """
    # Run checks
    checks = [
        FormatCheck(),
        LintCheck(),
        TypeCheck(),
        TestCheck(),
        SecretCheck(),
    ]
    
    for check in checks:
        result = check.run()
        if not result.passed:
            return HookResult(success=False, message=result.message)
    
    return HookResult(success=True)
```

## Remote Operations

### Remote Management

```python
class RemoteManager:
    """Manage remote repositories."""
    
    def add_remote(
        self,
        name: str,
        url: str,
        fetch: bool = True
    ) -> Remote:
        """Add remote repository."""
        
    def remove_remote(self, name: str) -> None:
        """Remove remote."""
        
    def fetch(
        self,
        remote: str = "origin",
        prune: bool = True,
        tags: bool = True
    ) -> FetchResult:
        """Fetch from remote."""
        
    def pull(
        self,
        remote: str = "origin",
        branch: str = None,
        rebase: bool = False
    ) -> PullResult:
        """Pull from remote."""
        
    def push(
        self,
        remote: str = "origin",
        branch: str = None,
        force: bool = False,
        set_upstream: bool = False
    ) -> PushResult:
        """Push to remote."""
```

## Error Handling

### Git Errors

```python
class GitError(Exception):
    """Base Git error."""
    
class BranchExistsError(GitError):
    """Branch already exists."""
    
class MergeConflictError(GitError):
    """Merge conflict detected."""
    
class DetachedHeadError(GitError):
    """Detached HEAD state."""
    
class UncommittedChangesError(GitError):
    """Uncommitted changes preventing operation."""
    
class BranchProtectionError(GitError):
    """Branch protection violation."""
```

### Error Recovery

```python
class ErrorRecovery:
    """Recover from Git errors."""
    
    def recover(self, error: GitError) -> RecoveryResult:
        """
        Attempt to recover from error.
        
        Strategies:
        - Stash changes
        - Abort operation
        - Reset to known state
        - Create recovery branch
        """
```

## Testing

### Unit Tests

```python
def test_create_branch():
    """Test branch creation."""
    git = GitManager(repo_path=test_repo)
    
    # Create branch
    branch = git.create_branch("test-branch")
    
    assert branch.name == "test-branch"
    assert branch.exists
    
    # Cleanup
    git.delete_branch("test-branch")

def test_merge_with_conflicts():
    """Test merge conflict handling."""
    git = GitManager(repo_path=test_repo)
    
    # Create conflicting changes
    # ... setup ...
    
    # Attempt merge
    result = git.merge("conflict-branch")
    
    assert result.has_conflicts
    
    # Resolve conflicts
    resolutions = git.ai_resolve_conflicts(result.conflicts)
    git.apply_resolutions(resolutions)
    
    # Verify resolution
    status = git.status()
    assert not status.conflicts
```

## Integration Examples

### With Aider

```python
from aider import AiderClient
from openclaw.integrations.aider.git import GitManager

# Initialize
aider = AiderClient()
git = GitManager()

# Get changes
diff = git.diff()

# Have Aider analyze changes
analysis = aider.analyze_changes(diff)

# Create branch for changes
branch = git.create_branch(f"fix/{analysis.category}")

# Commit with AI-generated message
message = aider.generate_commit_message(diff)
git.commit(message)
```

### With Review Module

```python
from openclaw.integrations.aider.review import ReviewManager
from openclaw.integrations.aider.git import GitManager

# Get changes for review
git = GitManager()
diff = git.diff("main", "HEAD")

# Review changes
review = ReviewManager()
result = review.review_changes(diff)

# Apply suggested fixes
for fix in result.fixes:
    # Apply fix
    pass

# Commit fixes
git.add(all=True)
git.commit("fix: apply review suggestions")
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-16
