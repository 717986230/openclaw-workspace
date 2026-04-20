# Aider Code Review Integration

## Overview

This module provides AI-powered code review capabilities integrated with Aider. It automates code quality checks, security analysis, and best practice enforcement.

## Features

### Automated Review

- Code style and convention checking
- Security vulnerability detection
- Performance optimization suggestions
- Documentation completeness verification
- Test coverage analysis

### Review Types

1. **Pre-commit Review:** Review before committing
2. **Pull Request Review:** Review PR changes
3. **Branch Review:** Compare branch against base
4. **Full Repository Review:** Complete codebase scan

### Review Rules

- Configurable rule sets
- Severity levels (Critical, Warning, Info)
- Auto-fix capabilities
- Exception handling

## Quick Start

### Basic Review

```python
from openclaw.integrations.aider.review import ReviewManager

# Initialize
review = ReviewManager(repo_path="/path/to/repo")

# Review current changes
result = review.review_changes(scope="changed")

# Print findings
for finding in result.findings:
    print(f"[{finding.severity}] {finding.file}:{finding.line}")
    print(f"  {finding.message}")
    print(f"  Suggestion: {finding.suggestion}")
```

### Pull Request Review

```python
# Review pull request
result = review.review_pr(pr_number=42)

# Post review as PR comment
review.post_pr_comments(result)
```

### Branch Review

```python
# Compare branch against main
result = review.review_branch(
    branch="feature/user-auth",
    base="main"
)

# Generate review report
report = result.generate_report()
print(report)
```

## Review Categories

### 1. Code Quality

```python
class CodeQualityReview:
    """Review code quality aspects."""
    
    rules = [
        ComplexityRule(max_cyclomatic=10),
        DuplicationRule(max_lines=50),
        NamingRule(convention="snake_case"),
        FunctionLengthRule(max_lines=50),
        ParameterCountRule(max_params=5),
    ]
```

### 2. Security

```python
class SecurityReview:
    """Review for security issues."""
    
    rules = [
        SQLInjectionRule(),
        XSSRule(),
        HardcodedSecretsRule(),
        InsecureDependencyRule(),
        AuthenticationRule(),
        AuthorizationRule(),
    ]
```

### 3. Performance

```python
class PerformanceReview:
    """Review for performance issues."""
    
    rules = [
        NPlusOneQueryRule(),
        MemoryLeakRule(),
        InefficientLoopRule(),
        UnoptimizedDatabaseRule(),
        CachingOpportunityRule(),
    ]
```

### 4. Documentation

```python
class DocumentationReview:
    """Review documentation completeness."""
    
    rules = [
        DocstringRule(required=True),
        READMErule(),
        APIChangesRule(),
        DeprecatedAnnotationRule(),
        TypeHintRule(),
    ]
```

### 5. Testing

```python
class TestReview:
    """Review test coverage and quality."""
    
    rules = [
        CoverageRule(min_coverage=80),
        TestNamingRule(),
        AssertionRule(),
        MockUsageRule(),
        EdgeCaseRule(),
    ]
```

## Configuration

### Review Config

```yaml
aider:
  review:
    enabled: true
    
    # Review scopes
    scopes:
      pre_commit: true
      pre_push: true
      pr: true
    
    # Categories to check
    categories:
      - quality
      - security
      - performance
      - documentation
      - testing
    
    # Severity levels
    fail_on:
      - critical
      - warning
    
    # Auto-fix
    auto_fix:
      enabled: true
      safe_only: true
    
    # File patterns
    include:
      - "**/*.py"
      - "**/*.js"
      - "**/*.ts"
    
    exclude:
      - "**/test/**"
      - "**/vendor/**"
      - "**/dist/**"
```

### Custom Rules

```yaml
aider:
  review:
    custom_rules:
      - name: "no-console-log"
        pattern: "console\\.log\\("
        message: "Remove console.log before commit"
        severity: warning
        
      - name: "require-todo"
        pattern: "TODO:"
        message: "Resolve TODO items"
        severity: info
```

## API Reference

### ReviewManager

```python
class ReviewManager:
    """Manage code review operations."""
    
    def __init__(
        self,
        repo_path: str = ".",
        config: ReviewConfig = None
    ):
        """Initialize review manager."""
        
    def review_changes(
        self,
        scope: str = "changed"
    ) -> ReviewResult:
        """
        Review changes.
        
        Args:
            scope: 'changed', 'staged', or 'all'
            
        Returns:
            ReviewResult with findings
        """
        
    def review_branch(
        self,
        branch: str,
        base: str = "main"
    ) -> ReviewResult:
        """Review branch against base."""
        
    def review_pr(
        self,
        pr_number: int
    ) -> ReviewResult:
        """Review pull request."""
        
    def review_file(
        self,
        path: str
    ) -> ReviewResult:
        """Review single file."""
        
    def apply_fixes(
        self,
        findings: List[Finding],
        safe_only: bool = True
    ) -> List[FixResult]:
        """Apply auto-fixes for findings."""
```

### ReviewResult

```python
@dataclass
class ReviewResult:
    findings: List[Finding]
    stats: ReviewStats
    passed: bool
    
    def generate_report(self) -> str:
        """Generate formatted report."""
        
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        
    def filter_by_severity(
        self,
        severity: Severity
    ) -> List[Finding]:
        """Filter findings by severity."""
```

### Finding

```python
@dataclass
class Finding:
    rule: str
    severity: Severity
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    auto_fixable: bool
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
```

## Review Workflow

### Pre-commit Review

```python
# Git pre-commit hook
def pre_commit_review():
    review = ReviewManager()
    result = review.review_changes(scope="staged")
    
    if not result.passed:
        # Print findings
        print(result.generate_report())
        
        # Offer to auto-fix
        if result.has_auto_fixable:
            print("\nAuto-fix available. Run: aider-review --fix")
        
        return False
    
    return True
```

### Pull Request Review

```python
def review_pull_request(pr_number: int):
    """Review and comment on PR."""
    review = ReviewManager()
    
    # Review PR
    result = review.review_pr(pr_number)
    
    # Post inline comments
    for finding in result.findings:
        review.post_pr_comment(
            pr_number=pr_number,
            file=finding.file,
            line=finding.line,
            body=format_finding(finding)
        )
    
    # Post summary
    review.post_pr_summary(
        pr_number=pr_number,
        body=result.generate_report()
    )
```

### Continuous Review

```python
def continuous_review():
    """Monitor and review changes continuously."""
    review = ReviewManager()
    
    # Watch for changes
    watcher = review.watch_changes()
    
    for event in watcher:
        if event.type == "file_changed":
            # Review changed file
            result = review.review_file(event.file)
            
            if result.has_critical:
                # Alert developer
                notify_critical_findings(result)
```

## Examples

### Integration with Git Hooks

```python
# .git/hooks/pre-commit
#!/usr/bin/env python3
from openclaw.integrations.aider.review import ReviewManager

def main():
    review = ReviewManager()
    result = review.review_changes(scope="staged")
    
    if result.has_critical:
        print("Critical issues found:")
        for finding in result.filter_by_severity(Severity.CRITICAL):
            print(f"  {finding.file}:{finding.line} - {finding.message}")
        return 1
    
    if result.has_warnings:
        print("Warnings found. Run 'aider-review --staged' for details.")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

### Custom Review Rule

```python
from openclaw.integrations.aider.review import ReviewRule, Severity

class NoTodoRule(ReviewRule):
    """Check for unresolved TODOs."""
    
    name = "no-todo"
    severity = Severity.INFO
    
    def check(self, file: str, content: str) -> List[Finding]:
        findings = []
        
        for i, line in enumerate(content.split('\n'), 1):
            if 'TODO' in line or 'FIXME' in line:
                findings.append(Finding(
                    rule=self.name,
                    severity=self.severity,
                    file=file,
                    line=i,
                    column=line.index('TODO') + 1,
                    message="Unresolved TODO/FIXME",
                    suggestion="Resolve or create issue for TODO"
                ))
        
        return findings

# Register rule
review = ReviewManager()
review.add_rule(NoTodoRule())
```

## Best Practices

1. **Run Early:** Review early in development cycle
2. **Fix Critical First:** Address critical issues before warnings
3. **Customize Rules:** Tailor rules to project needs
4. **Auto-fix Safely:** Use auto-fix for safe changes only
5. **Track Trends:** Monitor review metrics over time
6. **Educate Team:** Share findings to improve code quality

## Output Formats

### Text Report

```
=== Code Review Report ===

Files Reviewed: 15
Total Findings: 8

Critical: 1
Warning: 4
Info: 3

Critical Issues:
  src/auth.py:42 - SQL Injection vulnerability
    Use parameterized queries instead of string formatting
    
Warnings:
  src/user.py:120 - Function too complex (cyclomatic=15)
    Consider breaking into smaller functions
    
  src/api.py:50 - Missing docstring
    Add docstring for function 'process_request'
```

### JSON Report

```json
{
  "summary": {
    "files_reviewed": 15,
    "total_findings": 8,
    "critical": 1,
    "warning": 4,
    "info": 3
  },
  "findings": [
    {
      "rule": "sql-injection",
      "severity": "critical",
      "file": "src/auth.py",
      "line": 42,
      "message": "SQL Injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ]
}
```

### HTML Report

Generates interactive HTML report with:
- Summary dashboard
- File-by-file breakdown
- Severity filtering
- Source code highlighting

## Troubleshooting

### Slow Reviews

- Reduce file patterns
- Exclude generated code
- Cache analysis results
- Use incremental review

### False Positives

- Add suppression comments
- Adjust rule sensitivity
- Create custom exceptions
- Report and fix rules

### Integration Issues

- Check Git access
- Verify file permissions
- Ensure dependencies installed
- Check API connectivity

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-16
