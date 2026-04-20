# Test Runner Framework

## Overview

The Test Runner Framework provides a unified interface for executing tests across different testing frameworks and environments.

## Supported Frameworks

### Python

```yaml
frameworks:
  pytest:
    command: pytest
    config: pytest.ini
    options:
      - verbose: -v
      - coverage: --cov=src
      - parallel: -n auto
      - html_report: --html=report.html
      
  unittest:
    command: python -m unittest
    options:
      - verbose: -v
      - pattern: -p "test_*.py"
      
  nose2:
    command: nose2
    options:
      - verbose: -v
      - coverage: --with-coverage
```

### JavaScript/TypeScript

```yaml
frameworks:
  jest:
    command: npx jest
    config: jest.config.js
    options:
      - coverage: --coverage
      - parallel: --maxWorkers=4
      - watch: --watch
      
  vitest:
    command: npx vitest
    options:
      - coverage: --coverage
      - ui: --ui
      
  mocha:
    command: npx mocha
    options:
      - reporter: --reporter spec
      - coverage: nyc mocha
```

### Java

```yaml
frameworks:
  junit:
    command: mvn test
    options:
      - class: -Dtest=TestClassName
      - method: -Dtest=TestClassName#testMethod
      
  testng:
    command: mvn test -Dtestng
    config: testng.xml
```

## Runner Configuration

### Basic Configuration

```python
from openclaw.integrations.opendevin import TestRunner

runner = TestRunner(
    framework="pytest",
    config={
        "test_path": "./tests",
        "source_path": "./src",
        "parallel": True,
        "coverage": True,
        "verbose": True,
        "timeout": 300
    }
)
```

### Advanced Configuration

```yaml
# test-runner.yaml
runner:
  framework: pytest
  
  execution:
    parallel: true
    max_workers: 4
    batch_size: 10
    fail_fast: false
    
  timeout:
    global: 600        # 10 minutes total
    per_test: 60       # 1 minute per test
    per_class: 300     # 5 minutes per class
    
  coverage:
    enabled: true
    branch: true
    exclude:
      - "*/migrations/*"
      - "*/tests/*"
      - "*/__init__.py"
      
  reporting:
    formats:
      - junit-xml
      - html
      - json
    output_dir: ./test-results
    attach_on_failure: true
    
  environment:
    env_vars:
      TESTING: "true"
      DATABASE_URL: "sqlite:///:memory:"
    setup_commands:
      - pip install -r requirements-test.txt
    teardown_commands:
      - rm -rf /tmp/test_*
```

## Execution Modes

### 1. Local Execution

```python
# Run tests locally
result = runner.run_local(
    tests=["test_auth.py", "test_api.py"],
    options={"parallel": True}
)
```

### 2. Container Execution

```python
# Run in Docker container
result = runner.run_in_container(
    image="python:3.11",
    tests=["test_auth.py"],
    volume_mounts={
        "./src": "/app/src",
        "./tests": "/app/tests"
    }
)
```

### 3. Remote Execution

```python
# Run on remote host
result = runner.run_remote(
    host="test-server.example.com",
    tests=["test_auth.py"],
    sync_files=True
)
```

### 4. Distributed Execution

```python
# Run across multiple nodes
result = runner.run_distributed(
    tests=["test_*.py"],
    nodes=[
        {"host": "node1.example.com", "workers": 4},
        {"host": "node2.example.com", "workers": 4}
    ],
    strategy="load_balance"  # or "shard", "duplicate"
)
```

## Test Selection

### By Pattern

```python
# Select tests by pattern
result = runner.run(
    pattern="test_auth_*.py",
    exclude="*_slow.py"
)
```

### By Markers/Tags

```python
# Run tests with specific markers
result = runner.run(
    markers=["unit", "fast"],
    exclude_markers=["integration", "slow"]
)
```

### By Changed Files

```python
# Run tests affected by changes
result = runner.run_affected(
    changed_files=["src/auth.py", "src/api.py"],
    test_mapping="./.test-mapping.json"
)
```

### By Priority

```python
# Run high priority tests first
result = runner.run_priority(
    priority_order=["smoke", "unit", "integration"]
)
```

## Result Handling

### Result Object

```python
class TestResult:
    # Counts
    total: int
    passed: int
    failed: int
    skipped: int
    
    # Timing
    duration: float
    start_time: datetime
    end_time: datetime
    
    # Coverage
    coverage: CoverageReport
    
    # Details
    test_cases: List[TestCaseResult]
    failures: List[TestFailure]
    errors: List[TestError]
    
    # Artifacts
    logs: List[str]
    screenshots: List[bytes]
    attachments: Dict[str, bytes]
```

### Accessing Results

```python
result = runner.run()

# Summary
print(f"Tests: {result.total}")
print(f"Passed: {result.passed}")
print(f"Failed: {result.failed}")
print(f"Duration: {result.duration}s")
print(f"Coverage: {result.coverage.line_coverage}%")

# Failed tests
for failure in result.failures:
    print(f"Failed: {failure.name}")
    print(f"Error: {failure.message}")
    print(f"Traceback: {failure.traceback}")
```

### Result Export

```python
# Export in various formats
result.export(
    format="junit-xml",
    path="./test-results/junit.xml"
)

result.export(
    format="html",
    path="./test-results/report.html"
)

result.export(
    format="json",
    path="./test-results/results.json"
)
```

## Parallel Execution

### Worker Management

```python
# Configure parallel execution
runner = TestRunner(
    parallel=True,
    max_workers=8,
    worker_type="process"  # or "thread", "greenlet"
)

# Or dynamic workers based on CPU
runner = TestRunner(
    parallel=True,
    max_workers="auto"  # Uses CPU count
)
```

### Load Balancing

```yaml
parallel:
  strategy: load_balance
  
  # Distribute based on estimated duration
  estimation:
    method: historical  # or "file_size", "annotation"
    history_file: ./test-durations.json
    
  # Rebalancing
  rebalance: true
  rebalance_interval: 10s
```

### Test Isolation

```yaml
isolation:
  # Each test in separate process
  process_isolation: true
  
  # Database isolation
  database:
    transaction_per_test: true
    reset_sequences: true
    
  # File system isolation
  filesystem:
    temp_dir_per_test: true
    cleanup_after: true
```

## Retry & Recovery

### Automatic Retry

```yaml
retry:
  enabled: true
  max_retries: 3
  retry_delay: 5
  
  conditions:
    - type: ConnectionError
    - type: TimeoutError
    - flaky_test: true
      
  strategy: exponential_backoff
  backoff_factor: 2
```

### Failure Recovery

```python
# Resume from failure
result = runner.run(resume_from="./test-results/checkpoint.json")

# Skip known failures
result = runner.run(
    skip_known_failures="./known-failures.json"
)
```

## Hooks & Plugins

### Lifecycle Hooks

```python
class CustomRunner(TestRunner):
    @hook
    def before_test(self, test):
        # Setup before each test
        pass
    
    @hook
    def after_test(self, test, result):
