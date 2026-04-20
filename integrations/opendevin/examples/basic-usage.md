# Basic Usage Examples

## Overview

This document provides practical examples of using OpenDevin integration with OpenClaw for common development tasks.

## Installation

### Prerequisites

```bash
# Ensure Docker is running
docker --version

# Ensure OpenClaw is installed
openclaw --version

# Install OpenDevin integration
openclaw plugin install opendevin
```

### Configuration

```bash
# Configure OpenDevin
openclaw opendevin config set model claude-3-opus
openclaw opendevin config set sandbox docker
openclaw opendevin config set max_iterations 100

# Verify configuration
openclaw opendevin config list
```

## Example 1: Generate a New Module

### Command Line

```bash
# Generate a Python module from specification
openclaw opendevin generate \
  --spec "Create a user authentication module with login, logout, and session management" \
  --language python \
  --framework fastapi \
  --output ./src/auth
```

### Programmatic

```python
from openclaw.integrations.opendevin import OpenDevinAgent

# Initialize agent
agent = OpenDevinAgent()

# Generate code
result = agent.generate(
    spec="""
    Create a user authentication module with:
    - Login endpoint (POST /auth/login)
    - Logout endpoint (POST /auth/logout)
    - Session validation middleware
    - JWT token generation and validation
    """,
    language="python",
    framework="fastapi",
    output_path="./src/auth"
)

# Review generated code
for file in result.files:
    print(f"Generated: {file.path}")
    print(f"Lines: {file.line_count}")
    print(f"Preview:\n{file.content[:500]}...")

# Close agent
agent.close()
```

## Example 2: Fix a Bug

### Command Line

```bash
# Let OpenDevin analyze and fix a bug
openclaw opendevin fix \
  --file ./src/api.py \
  --issue "TypeError when user_id is None in get_user endpoint"
```

### Programmatic

```python
from openclaw.integrations.opendevin import OpenDevinAgent

agent = OpenDevinAgent()

# Analyze and fix bug
result = agent.fix(
    file_path="./src/api.py",
    issue_description="""
    TypeError occurs when calling get_user endpoint with user_id=None.
    Error message: 'NoneType' object has no attribute 'id'
    Expected: Return 404 Not Found response
    """,
    test_before_fix=True  # Run tests before and after
)

print(f"Bug fixed: {result.fixed}")
print(f"Changes made: {result.changes}")
print(f"Tests passing: {result.tests_passed}")

agent.close()
```

## Example 3: Generate Tests

### Command Line

```bash
# Generate tests for existing code
openclaw opendevin test-generate \
  --source ./src/auth.py \
  --output ./tests/test_auth.py \
  --framework pytest \
  --coverage-target 80
```

### Programmatic

```python
from openclaw.integrations.opendevin import TestAgent

agent = TestAgent()

# Generate tests
tests = agent.generate_tests(
    source_path="./src/auth.py",
    options={
        "framework": "pytest",
        "include_edge_cases": True,
        "mock_external": True,
        "coverage_target": 80
    }
)

# Review generated tests
print(f"Generated {len(tests.test_cases)} test cases")
for test in tests.test_cases:
    print(f"  - {test.name}: {test.description}")

# Save tests
tests.save("./tests/test_auth.py")

agent.close()
```

## Example 4: Run Tests with Coverage

### Command Line

```bash
# Run tests with coverage analysis
openclaw opendevin test \
  --path ./tests \
  --coverage \
  --report html \
  --output ./test-results

# View coverage report
open coverage/html/index.html
```

### Programmatic

```python
from openclaw.integrations.opendevin import TestRunner

runner = TestRunner()

# Run tests
result = runner.run(
    test_path="./tests",
    options={
        "parallel": True,
        "coverage": True,
        "report_format": "html"
    }
)

# Check results
print(f"Tests: {result.total}")
print(f"Passed: {result.passed}")
print(f"Failed: {result.failed}")
print(f"Coverage: {result.coverage.line_coverage}%")

# Access detailed coverage data
for file in result.coverage.files:
    if file.coverage < 80:
        print(f"Low coverage: {file.path} ({file.coverage}%)")

runner.close()
```

## Example 5: Refactor Code

### Command Line

```bash
# Refactor code for better performance
openclaw opendevin refactor \
  --path ./src/legacy_code.py \
  --goal "improve performance" \
  --preserve-behavior
```

### Programmatic

```python
from openclaw.integrations.opendevin import OpenDevinAgent

agent = OpenDevinAgent()

# Refactor code
result = agent.refactor(
    path="./src/legacy_code.py",
    goal="improve performance and readability",
    constraints={
        "preserve_behavior": True,
        "maintain_api": True
    }
)

# Review changes
print(f"Original: {result.original_metrics}")
print(f"Refactored: {result.new_metrics}")
print(f"Improvement: {result.improvement_summary}")

# View diff
print(result.diff)

# Apply changes
result.apply()

agent.close()
```

## Example 6: Code Review

### Command Line

```bash
# Perform automated code review
openclaw opendevin review \
  --path ./src/new_feature.py \
  --check security,performance,best-practices
```

### Programmatic

```python
from openclaw.integrations.opendevin import ReviewAgent

agent = ReviewAgent()

# Review code
review = agent.review(
    path="./src/new_feature.py",
    checks=["security", "performance", "best-practices", "style"]
)

# View findings
for finding in review.findings:
    print(f"[{finding.severity}] {finding.category}")
    print(f"  Location: {finding.location}")
    print(f"  Issue: {finding.message}")
    print(f"  Suggestion: {finding.suggestion}")

# Get summary
print(f"Total findings: {len(review.findings)}")
print(f"Critical: {review.critical_count}")
print(f"Warnings: {review.warning_count}")

agent.close()
```

## Example 7: Full Development Workflow

```python
from openclaw.integrations.opendevin import (
    OpenDevinAgent,
    TestAgent,
    ReviewAgent
)

# Initialize agents
dev_agent = OpenDevinAgent()
test_agent = TestAgent()
review_agent = ReviewAgent()

# Step 1: Generate code
print("Generating code...")
code_result = dev_agent.generate(
    spec="""
    Create a REST API for task management with:
    - CRUD operations for tasks
    - Task assignment to users
    - Task status tracking
    - Due date management
    """,
    language="python",
    framework="fastapi",
    output_path="./src/tasks"
)

# Step 2: Generate tests
print("Generating tests...")
test_result = test_agent.generate_tests(
    source_path="./src/tasks",
    options={"coverage_target": 85}
)

# Step 3: Run tests
print("Running tests...")
run_result = test_agent.run_tests("./tests")
print(f"Tests passed: {run_result.passed}/{run_result.total}")
print(f"Coverage: {run_result.coverage}%")

# Step 4: Review code
print("Reviewing code...")
review_result = review_agent.review("./src/tasks")
print(f"Findings: {len(review_result.findings)}")

# Step 5: Fix issues
if review_result.has_critical:
    print("Fixing critical issues...")
    for finding in review_result.critical_findings:
        dev_agent.fix(
            file_path=finding.location.file,
            issue_description=finding.message
        )

# Step 6: Final validation
print("Final validation...")
final_result = test_agent.run_tests("./tests")
print(f"Final test results: {final_result.passed}/{final_result.total}")
print(f"Final coverage: {final_result.coverage}%")

# Cleanup
dev_agent.close()
test_agent.close()
review_agent.close()
```

## Example 8: Environment Management

```python
from openclaw.integrations.opendevin import EnvironmentManager

manager = EnvironmentManager()

# Create development environment
env = manager.create(
    name="my-project-dev",
    template="python-fastapi",
    config={
        "python_version": "3.11",
        "packages": ["fastapi", "uvicorn", "pytest"]
    }
)

# Start environment
env.start()

# Execute commands
result = env.execute("pip install -r requirements.txt")
result = env.execute("python -m pytest tests/")

# Create snapshot
snapshot = env.snapshot(name="before-refactor")

# Make changes...
env.execute("python refactor.py