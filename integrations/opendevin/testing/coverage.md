# Test Coverage Analysis

## Overview

Coverage analysis measures how much of the source code is executed during testing, helping identify gaps in test quality.

## Coverage Types

### Line Coverage

Percentage of code lines executed:

```python
from openclaw.integrations.opendevin import CoverageAnalyzer

analyzer = CoverageAnalyzer()

# Measure line coverage
result = analyzer.measure(
    source_path="./src",
    test_path="./tests",
    type="line"
)

print(f"Line coverage: {result.coverage}%")
print(f"Uncovered lines: {result.uncovered}")
```

### Branch Coverage

Percentage of code branches taken:

```python
# Measure branch coverage
result = analyzer.measure(
    source_path="./src",
    test_path="./tests",
    type="branch"
)

print(f"Branch coverage: {result.coverage}%")
print(f"Branches: {result.total_branches}")
print(f"Taken: {result.branches_taken}")
print(f"Not taken: {result.branches_not_taken}")
```

### Function Coverage

Percentage of functions called:

```python
# Measure function coverage
result = analyzer.measure(
    source_path="./src",
    test_path="./tests",
    type="function"
)

for func in result.functions:
    print(f"{func.name}: called {func.call_count} times")
```

### Statement Coverage

Percentage of statements executed:

```python
# Measure statement coverage
result = analyzer.measure(
    source_path="./src",
    test_path="./tests",
    type="statement"
)
```

## Coverage Configuration

### Basic Configuration

```yaml
coverage:
  type: line
  source: ./src
  tests: ./tests
  
  report:
    format: html
    output: ./coverage
```

### Advanced Configuration

```yaml
coverage:
  # Multiple coverage types
  types:
    - line
    - branch
    - function
    
  # Source paths
  source:
    - ./src
    - ./lib
    
  # Test paths
  tests:
    - ./tests
    - ./integration_tests
    
  # Exclusions
  exclude:
    patterns:
      - "*/migrations/*"
      - "*/tests/*"
      - "*/__init__.py"
      - "*/config/*"
    functions:
      - "__repr__"
      - "__str__"
      
  # Inclusions
  include:
    patterns:
      - "*/models/*"
      - "*/views/*"
      
  # Reporting
  report:
    formats:
      - html
      - xml
      - json
      - lcov
    output: ./coverage-reports
    
  # Thresholds
  thresholds:
    minimum:
      line: 80
      branch: 70
      function: 90
    fail_below: true
```

## Coverage Analysis

### Gap Analysis

```python
# Analyze coverage gaps
gaps = analyzer.find_gaps(
    source_path="./src",
    test_path="./tests",
    threshold=80
)

for gap in gaps:
    print(f"File: {gap.file}")
    print(f"Uncovered: {gap.uncovered_lines}")
    print(f"Coverage: {gap.coverage}%")
    print(f"Suggested tests: {gap.suggested_tests}")
```

### Diff Coverage

```python
# Coverage for changed code only
diff_coverage = analyzer.measure_diff(
    source_path="./src",
    base_branch="main",
    current_branch="feature/new-feature"
)

print(f"New code coverage: {diff_coverage.coverage}%")
print(f"Uncovered new lines: {diff_coverage.uncovered_new_lines}")
```

### Historical Analysis

```python
# Track coverage over time
history = analyzer.get_history(
    source_path="./src",
    days=30
)

for entry in history:
    print(f"{entry.date}: {entry.coverage}%")
    
# Plot trend
analyzer.plot_trend(history, output="./coverage-trend.png")
```

## Coverage Reports

### HTML Report

```python
# Generate HTML report
analyzer.generate_report(
    format="html",
    output="./coverage/html",
    options={
        "title": "Project Coverage",
        "include_source": True,
        "skip_empty": True
    }
)
```

### XML Report (Cobertura)

```python
# Generate XML report for CI tools
analyzer.generate_report(
    format="xml",
    output="./coverage/cobertura.xml"
)
```

### JSON Report

```python
# Generate JSON report
analyzer.generate_report(
    format="json",
    output="./coverage/coverage.json",
    options={
        "pretty": True,
        "include_details": True
    }
)
```

### LCOV Report

```python
# Generate LCOV report for IDE integration
analyzer.generate_report(
    format="lcov",
    output="./coverage/lcov.info"
)
```

## Integration with IDE

### VS Code Integration

```json
// .vscode/settings.json
{
  "coverage-gutters.customizable": {
    "lcovpath": "./coverage/lcov.info",
    "showGutterCoverage": true,
    "showLineCoverage": true,
    "showRulerCoverage": true
  }
}
```

### PyCharm Integration

```yaml
# Configure coverage in PyCharm
coverage:
  runner: pytest
  options:
    --cov: src
    --cov-report: html
```

## Coverage Enforcement

### Quality Gates

```yaml
# coverage-gates.yaml
gates:
  - name: minimum-coverage
    thresholds:
      line: 80
      branch: 70
      function: 90
    action: fail
    
  - name: no-degradation
    comparison: previous
    max_change: -5
    action: warn
    
  - name: new-code-covered
    type: diff
    threshold: 90
    action: fail
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: coverage-check
        name: Check coverage
        entry: openclaw opendevin coverage-check --minimum 80
        language: system
        types: [python]
        pass_filenames: false
```

### CI Integration

```yaml
# GitHub Actions
- name: Run coverage
  run: openclaw opendevin test --coverage --minimum 80

- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage/cobertura.xml
    fail_ci_if_error: true
```

## Advanced Features

### Coverage Merging

```python
# Merge coverage from multiple runs
analyzer.merge_coverage(
    files=[
        "./coverage/unit-tests.json",
        "./coverage/integration-tests.json",
        "./coverage/e2e-tests.json"
    ],
    output="./coverage/combined.json"
)
```

### Coverage Exclusions

```python
# pragma comments for exclusion
def debug_function():
    # pragma: no cover
    print("Debug output")  # Excluded from coverage

def conditional_debug():
    if DEBUG:  # pragma: no cover
        print("Debug mode")  # Excluded
    return result  # Covered
```

### Coverage Annotations

```python
# Annotate code with coverage requirements
@require_coverage(80)  # Minimum 80% coverage for this function
def important_function():
    pass

@require_branch_coverage(100)  # All branches must be covered
def critical_logic():
    pass
```

## Coverage Optimization

### Prioritization

```python
# Prioritize tests by coverage
prioritized = analyzer.prioritize_tests(
    test_path="./tests",
    source_path="./src",
    strategy="coverage_per_time"  # Maximize coverage per execution time
)

# Run prioritized tests
for test in prioritized[:10]:  # Top 10 tests
    print(f"{test.name}: coverage {test.coverage_gain}%")
```

### Minimization

```python
# Find minimal test set for full coverage
minimal_set = analyzer.find_minimal_set(
    test_path="./tests",
    source_path="./src"
)

print(f"Original tests: {len(analyzer.all_tests)}")
print(f"Minimal set: {len(minimal_set)}")
print(f"Reduction: {(1 - len(minimal_set)/len(analyzer.all_tests))*100}%")
```

## Best Practices

### 1. Set Realistic Goals

- Start with 60-70% for new projects
- Aim for 80%+ for mature code
- Focus on critical paths first
- Don't sacrifice quality for coverage

### 2. Focus on Quality

- High coverage ≠ good tests
- Test behavior, not implementation
- Include edge cases
- Avoid trivial tests for coverage

### 3. Monitor Trends

- Track coverage over time
- Watch for degradation
- Set up alerts
- Review coverage reports regularly

### 4. Use Coverage Tools

- IDE integration for visual feedback
- CI integration for enforcement
- Pre-commit hooks for early detection
- Coverage reports for analysis

## Troubleshooting

### Low Coverage

**Causes:**
- Missing test cases
- Dead code
- Complex conditionals
- External dependencies

**Solutions:**
- Add tests for uncovered code
- Remove unused code
- Simplify conditionals
- Mock external dependencies

### Inconsistent Coverage

**Causes:**
- Flaky tests
- Non-deterministic code
- Parallel test execution

**Solutions:**
- Fix flaky tests
- Make tests deterministic
- Proper test isolation

### Coverage Not Increasing

**Causes:**
- Testing wrong paths
- Excluded files
- Coverage configuration issues

**Solutions:**
- Verify test execution
- Check exclusions
- Review coverage configuration
