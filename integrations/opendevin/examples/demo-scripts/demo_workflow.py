#!/usr/bin/env python3
"""
Demo script for OpenDevin workflow
Shows how to use OpenDevin for code generation and testing
"""

import os
import sys
import json
import time
from pathlib import Path

# Add integration path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def demo_code_generation():
    """Demonstrate code generation capabilities."""
    print("\n" + "="*60)
    print("Demo: Code Generation")
    print("="*60)
    
    from openclaw.integrations.opendevin import OpenDevinAgent
    
    agent = OpenDevinAgent()
    
    # Generate a Python module
    print("\nGenerating a data validation module...")
    result = agent.generate(
        spec="""
        Create a Python module for data validation with:
        - Email validation
        - Phone number validation (international format)
        - URL validation
        - Date validation
        - Custom regex validation
        All with comprehensive error messages.
        """,
        language="python",
        output_path="./generated/validators.py"
    )
    
    print(f"\nGenerated files:")
    for file in result.files:
        print(f"  - {file.path}")
        print(f"    Lines: {file.line_count}")
    
    agent.close()
    return result


def demo_test_generation():
    """Demonstrate test generation."""
    print("\n" + "="*60)
    print("Demo: Test Generation")
    print("="*60)
    
    from openclaw.integrations.opendevin import TestAgent
    
    agent = TestAgent()
    
    # Generate tests for sample app
    print("\nGenerating tests for sample_fastapi_app.py...")
    result = agent.generate_tests(
        source_path="./examples/sample-project/sample_fastapi_app.py",
        options={
            "framework": "pytest",
            "include_edge_cases": True,
            "coverage_target": 85
        }
    )
    
    print(f"\nGenerated {len(result.test_cases)} test cases:")
    for test in result.test_cases[:5]:  # Show first 5
        print(f"  - {test.name}")
    
    if len(result.test_cases) > 5:
        print(f"  ... and {len(result.test_cases) - 5} more")
    
    # Save generated tests
    result.save("./generated/test_validators.py")
    print(f"\nTests saved to: ./generated/test_validators.py")
    
    agent.close()
    return result


def demo_test_execution():
    """Demonstrate test execution."""
    print("\n" + "="*60)
    print("Demo: Test Execution")
    print("="*60)
    
    from openclaw.integrations.opendevin import TestRunner
    
    runner = TestRunner()
    
    # Run tests with coverage
    print("\nRunning tests with coverage analysis...")
    result = runner.run(
        test_path="./examples/sample-project",
        options={
            "parallel": True,
            "coverage": True,
            "verbose": True
        }
    )
    
    print(f"\nTest Results:")
    print(f"  Total: {result.total}")
    print(f"  Passed: {result.passed}")
    print(f"  Failed: {result.failed}")
    print(f"  Skipped: {result.skipped}")
    print(f"  Duration: {result.duration:.2f}s")
    print(f"  Coverage: {result.coverage.line_coverage}%")
    
    if result.failures:
        print(f"\nFailures:")
        for failure in result.failures:
            print(f"  - {failure.name}: {failure.message}")
    
    runner.close()
    return result


def demo_code_refactoring():
    """Demonstrate code refactoring."""
    print("\n" + "="*60)
    print("Demo: Code Refactoring")
    print("="*60)
    
    from openclaw.integrations.opendevin import OpenDevinAgent
    
    agent = OpenDevinAgent()
    
    # Refactor code
    print("\nRefactoring code for better performance...")
    result = agent.refactor(
        path="./examples/sample-project/sample_fastapi_app.py",
        goal="improve performance and add caching",
        constraints={
            "preserve_behavior": True,
            "maintain_api": True
        }
    )
    
    print(f"\nRefactoring Results:")
    print(f"  Original complexity: {result.original_metrics.complexity}")
    print(f"  New complexity: {result.new_metrics.complexity}")
    print(f"  Improvements: {result.improvement_summary}")
    
    agent.close()
    return result


def demo_environment_management():
    """Demonstrate environment management."""
    print("\n" + "="*60)
    print("Demo: Environment Management")
    print("="*60)
    
    from openclaw.integrations.opendevin import EnvironmentManager
    
    manager = EnvironmentManager()
    
    # Create environment
    print("\nCreating development environment...")
    env = manager.create(
        name="demo-env",
        template="python-fastapi",
        config={
            "python_version": "3.11"
        }
    )
    
    print(f"  Environment created: {env.name}")
    
    # Start environment
    print("\nStarting environment...")
    env.start()
    print("  Environment started")
    
    # Execute command
    print("\nExecuting command...")
    result = env.execute("python --version")
    print(f"  Output: {result.stdout.strip()}")
    
    # Check status
    status = env.status()
    print(f"\nEnvironment Status:")
    print(f"  Running: {status.running}")
    print(f"  Memory: {status.memory_usage}%")
    print(f"  CPU: {status.cpu_usage}%")
    
    # Cleanup
    print("\nCleaning up...")
    env.stop()
    env.destroy()
    print("  Environment destroyed")
    
    manager.close()


def demo_coverage_analysis():
    """Demonstrate coverage analysis."""
    print("\n" + "="*60)
    print("Demo: Coverage Analysis")
    print("="*60)
    
    from openclaw.integrations.opendevin import CoverageAnalyzer
    
    analyzer = CoverageAnalyzer()
    
    # Analyze coverage
    print("\nAnalyzing test coverage...")
    result = analyzer.analyze(
        source_path="./examples/sample-project",
        test_path="./examples/sample-project",
        options={
            "branch_coverage": True
        }
    )
    
    print(f"\nCoverage Summary:")
    print(f"  Line coverage: {result.line_coverage}%")
    print(f"  Branch coverage: {result.branch_coverage}%")
    print(f"  Function coverage: {result.function_coverage}%")
    
    print(f"\nFiles with low coverage:")
    for file in result.files:
        if file.coverage < 80:
            print(f"  - {file.path}: {file.coverage}%")
    
    # Generate report
    print("\nGenerating HTML coverage report...")
    result.generate_report(
        format="html",
        output_path="./coverage/html"
    )
    print("  Report saved to: ./coverage/html/index.html")
    
    analyzer.close()


def run_full_workflow():
    """Run complete workflow demonstration."""
    print("\n" + "="*60)
    print("Full Workflow Demonstration")
    print("="*60)
    
    # Step 1: Generate code
    print("\n[1/5] Generating code...")
    code_result = demo_code_generation()
    
    # Step 2: Generate tests
    print("\n[2/5] Generating tests...")
    test_result = demo_test_generation()
    
    # Step 3: Run tests
    print("\n[3/5] Running tests...")
    run_result = demo_test_execution()
    
    # Step 4: Analyze coverage
    print("\n[4/5] Analyzing coverage...")
    demo_coverage_analysis()
    
    # Step 5: Generate report
    print("\n[5/5] Generating final report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "workflow": "full_demonstration",
        "results": {
            "code_generation": {
                "files_generated": len(code_result.files),
                "total_lines": sum(f.line_count for f in code_result.files)
            },
            "test_generation": {
                "tests_generated": len(test_result.test_cases)
            },
            "test_execution": {
                "total": run_result.total,
                "passed": run_result.passed,
                "failed": run_result.failed,
                "coverage": f"{run_result.coverage.line_coverage}%"
            }
        }
    }
    
    # Save report
    report_path = "./reports/workflow_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    print("\n" + "="*60)
    print("Workflow Complete!")
    print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenDevin Integration Demo"
    )
    parser.add_argument(
        '--demo',
        choices=[
            'generate', 'test-gen', 'test-run',
            'refactor', 'env', 'coverage', 'full'
        ],
        default='full',
        help='Demo to run'
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("./generated", exist_ok=True)
    os.makedirs("./reports", exist_ok=True)
    os.makedirs("./coverage", exist_ok=True)
    
    try:
        if args.demo == 'generate':
            demo_code_generation()
        elif args.demo == 'test-gen':
            demo_test_generation()
        elif args.demo == 'test