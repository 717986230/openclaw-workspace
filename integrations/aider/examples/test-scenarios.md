# Aider Integration Test Scenarios

## Overview

This document describes test scenarios for validating the Aider integration.

## Test Categories

### 1. Git Integration Tests

#### Test: Branch Creation and Deletion

```python
def test_branch_operations():
    """Test branch creation and deletion."""
    git = GitManager(repo_path=test_repo)
    
    # Create branch
    branch = git.create_branch("test-branch", base="main")
    assert branch.name == "test-branch"
    assert branch.base == "main"
    
    # List branches
    branches = git.list_branches()
    assert "test-branch" in [b.name for b in branches]
    
    # Switch branch
    git.switch_branch("test-branch")
    status = git.status()
    assert status.branch == "test-branch"
    
    # Delete branch
    git.switch_branch("main")
    git.delete_branch("test-branch")
    branches = git.list_branches()
    assert "test-branch" not in [b.name for b in branches]
```

#### Test: Merge Operations

```python
def test_merge_without_conflicts():
    """Test merge without conflicts."""
    git = GitManager(repo_path=test_repo)
    
    # Create feature branch with changes
    git.create_branch("feature-a")
    make_changes()
    git.add(all=True)
    git.commit("Feature A changes")
    
    # Merge to main
    git.switch_branch("main")
    result = git.merge("feature-a")
    
    assert result.success
    assert not result.has_conflicts

def test_merge_with_conflicts():
    """Test merge with AI conflict resolution."""
    git = GitManager(repo_path=test_repo)
    
    # Create conflicting changes
    git.create_branch("conflict-branch")
    make_conflicting_changes()
    git.add(all=True)
    git.commit("Conflicting changes")
    
    git.switch_branch("main")
    make_other_conflicting_changes()
    git.add(all=True)
    git.commit("Main changes")
    
    # Attempt merge
    result = git.merge("conflict-branch")
    
    assert result.has_conflicts
    
    # AI resolution
    resolutions = git.ai_resolve_conflicts(result.conflicts)
    git.apply_resolutions(resolutions)
    git.commit_merge("Merge conflict-branch")
    
    # Verify resolution
    status = git.status()
    assert not status.conflicts
```

### 2. Review Integration Tests

#### Test: Basic Review

```python
def test_basic_review():
    """Test basic code review."""
    review = ReviewManager(repo_path=test_repo)
    
    # Create file with issues
    create_file_with_issues()
    
    # Review file
    result = review.review_file("test_file.py")
    
    assert len(result.findings) > 0
    assert result.has_warnings or result.has_critical

def test_review_categories():
    """Test different review categories."""
    review = ReviewManager(repo_path=test_repo)
    
    # Create files with different issues
    create_security_issue_file()
    create_performance_issue_file()
    
    # Review with specific categories
    security_result = review.review_file(
        "security_issue.py",
        categories=["security"]
    )
    performance_result = review.review_file(
        "performance_issue.py",
        categories=["performance"]
    )
    
    assert security_result.has_security_findings
    assert performance_result.has_performance_findings
```

#### Test: Auto-fix

```python
def test_auto_fix():
    """Test auto-fix functionality."""
    review = ReviewManager(repo_path=test_repo)
    
    # Create file with auto-fixable issues
    create_file_with_fixable_issues()
    
    # Review and fix
    result = review.review_file("fixable.py")
    fixes = review.apply_fixes(result.findings, safe_only=True)
    
    # Verify fixes applied
    for fix in fixes:
        assert fix.applied
        assert fix.file == "fixable.py"
    
    # Re-review
    result2 = review.review_file("fixable.py")
    assert len(result2.findings) < len(result.findings)
```

### 3. Commit Integration Tests

#### Test: Message Generation

```python
def test_message_generation():
    """Test commit message generation."""
    commit = CommitManager(repo_path=test_repo)
    
    # Create feature changes
    create_feature_changes()
    git.add(["feature_file.py"])
    
    # Analyze and generate
    analysis = commit.analyze_staged()
    message = commit.generate_message(analysis)
    
    # Verify format
    assert message.startswith("feat")
    assert ":" in message
    assert len(message.split("\n")[0]) <= 72

def test_atomic_commits():
    """Test atomic commit grouping."""
    commit = CommitManager(repo_path=test_repo)
    
    # Create multiple unrelated changes
    create_multiple_changes()
    git.add(all=True)
    
    # Analyze and group
    analysis = commit.analyze_staged()
    groups = commit.group_changes(analysis)
    
    # Should create multiple groups
    assert len(groups) > 1
    
    # Each group should be atomic
    for group in groups:
        assert group.is_atomic
```

#### Test: Commit Workflow

```python
def test_complete_commit_workflow():
    """Test complete commit workflow."""
    commit = CommitManager(repo_path=test_repo)
    
    # Make changes
    create_changes()
    
    # Stage changes
    git.add(all=True)
    
    # Smart commit
    result = commit.smart_commit()
    
    assert result.success
    assert result.hash is not None
    assert result.message != ""
    
    # Verify commit exists
    commit_info = git.show_commit(result.hash)
    assert commit_info.message == result.message
```

### 4. Integration Tests

#### Test: Full Feature Workflow

```python
def test_full_feature_workflow():
    """Test complete feature development workflow."""
    # Initialize components
    git = GitManager(repo_path=test_repo)
    review = ReviewManager(repo_path=test_repo)
    commit = CommitManager(repo_path=test_repo)
    
    # Create branch
    git.create_branch("feature/test", base="main")
    git.switch_branch("feature/test")
    
    # Make changes
    create_feature_changes()
    git.add(all=True)
    
    # Review changes
    review_result = review.review_changes(scope="staged")
    assert not review_result.has_critical
    
    # Create commits
    analysis = commit.analyze_staged()
    groups = commit.group_changes(analysis)
    
    commit_hashes = []
    for group in groups:
        result = commit.commit_group(group)
        commit_hashes.append(result.hash)
    
    # Verify commits
    for hash in commit_hashes:
        info = git.show_commit(hash)
        assert info.hash == hash
    
    # Merge to main
    git.switch_branch("main")
    merge_result = git.merge("feature/test")
    assert merge_result.success
    
    # Cleanup
    git.delete_branch("feature/test")
```

#### Test: Error Handling

```python
def test_error_handling():
    """Test error handling in workflow."""
    git = GitManager(repo_path=test_repo)
    
    # Test invalid branch name
    with pytest.raises(InvalidBranchNameError):
        git.create_branch("invalid..branch")
    
    # Test merge conflict handling
    create_conflicts()
    result = git.merge("conflict-branch")
    assert result.has_conflicts
    
    # Test abort
    git.abort_merge()
    status = git.status()
    assert not status.in_merge

def test_rollback():
    """Test rollback functionality."""
    commit = CommitManager(repo_path=test_repo)
    
    # Make and commit changes
    create_changes()
    git.add(all=True)
    result = commit.smart_commit()
    
    # Rollback
    git.reset_hard("HEAD~1")
    
    # Verify rollback
    status = git.status()
    assert status.branch == "main"
    assert result.hash not in [c.hash for c in git.log()]
```

## Performance Tests

### Large Repository Test

```python
def test_large_repository():
    """Test performance with large repository."""
    git = GitManager(repo_path=large_repo)
    
    # Measure status time
    start = time.time()
    status = git.status()
    elapsed = time.time() - start
    
    assert elapsed < 5.0  # Should complete within 5 seconds

def test_large_diff_analysis():
    """Test diff analysis with many changes."""
    commit = CommitManager(repo_path=large_repo)
    
    # Create many changes
    create_many_changes(count=100)
    git.add(all=True)
    
    # Analyze
    start = time.time()
    analysis = commit.analyze_staged()
    elapsed = time.time() - start
    
    assert elapsed < 10.0
```

## Test Setup

### Fixtures

```python
@pytest.fixture
def test_repo(tmp_path):
    """Create test repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize Git
    subprocess.run(["git", "init"], cwd=repo_path)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path)
    
    # Create initial commit
    (repo_path / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path)
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(repo_path)

@pytest.fixture
def git(test_repo):
    """Create GitManager instance."""
    return GitManager(repo_path=str(test_repo))
```

## Running Tests

```bash
# Run all tests
pytest tests/integrations/aider/

# Run specific test file
pytest tests/integrations/aider/test_git.py

# Run with coverage
pytest tests/integrations/aider/ --cov=openclaw.integrations.aider

# Run specific test
pytest tests/integrations/aider/test_git.py::test_branch_operations
```

## Test Coverage Goals

- Git Integration: 80%+
- Review Integration: 85%+
- Commit Integration: 85%+
- Overall: 80%+

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-16
