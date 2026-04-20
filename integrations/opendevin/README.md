# OpenDevin Integration for OpenClaw

OpenDevin is an autonomous software engineering framework that enables AI-powered code generation, environment management, and test automation. This integration brings OpenDevin's capabilities into the OpenClaw ecosystem.

## Features

### 🔧 Code Generation
- Generate code from natural language specifications
- Multi-language support (Python, JavaScript, TypeScript, etc.)
- Framework-aware generation (FastAPI, Django, React, etc.)
- Context-aware code completion

### 🧪 Test Automation
- Automatic test generation
- Coverage analysis and reporting
- Support for pytest, unittest, jest, and more
- Test-driven development workflows

### 🐳 Environment Management
- Docker-based isolated environments
- Resource management and quotas
- Snapshot and restore capabilities
- Multi-container orchestration

### 🔒 Security
- Sandboxed code execution
- Network isolation
- User namespace separation
- Audit logging

## Quick Start

### Installation

```bash
# Install OpenDevin integration
openclaw plugin install opendevin

# Verify installation
openclaw opendevin --version
```

### Basic Usage

```bash
# Generate code
openclaw opendevin generate \
  --spec "Create a REST API for user management" \
  --language python \
  --framework fastapi

# Generate tests
openclaw opendevin test-generate \
  --source ./src/main.py \
  --output ./tests/test_main.py

# Run tests with coverage
openclaw opendevin test \
  --path ./tests \
  --coverage \
  --report html
```

## Documentation

- [Integration Guide](./INTEGRATION.md) - Complete integration documentation
- [Development Agent](./development/dev-agent.md) - Agent configuration and usage
- [Code Generation](./development/codegen.md) - Code generation workflows
- [Sandbox Setup](./development/sandbox.md) - Sandbox environment configuration
- [Environment Manager](./environment/env-manager.md) - Environment lifecycle management
- [Docker Setup](./environment/docker-setup.md) - Docker configuration
- [Runtime Configuration](./environment/runtime.md) - Runtime options
- [Test Agent](./testing/test-agent.md) - Testing automation
- [Test Runner](./testing/test-runner.md) - Test execution framework
- [Coverage Analysis](./testing/coverage.md) - Coverage configuration

## Examples

See [examples/](./examples/) directory for:

- Basic usage examples
- Sample FastAPI project
- Demo scripts

### Running Examples

```bash
# Navigate to examples
cd integrations/opendevin/examples/sample-project

# Install dependencies
pip install -r requirements.txt

# Run the application
python sample_fastapi_app.py

# Run tests
pytest test_sample_app.py -v

# Or use OpenDevin
openclaw opendevin test --path .
```

## Architecture

```
integrations/opendevin/
├── INTEGRATION.md          # Main integration documentation
├── README.md              # This file
├── development/           # Development tools
│   ├── dev-agent.md      # Agent configuration
│   ├── codegen.md        # Code generation
│   └── sandbox.md        # Sandbox environment
├── environment/           # Environment management
│   ├── env-manager.md    # Lifecycle management
│   ├── docker-setup.md   # Docker configuration
│   └── runtime.md        # Runtime options
├── testing/              # Testing automation
│   ├── test-agent.md     # Test agent
│   ├── test-runner.md    # Test execution
│   └── coverage.md       # Coverage analysis
└── examples/             # Example implementations
    ├── basic-usage.md    # Usage examples
    ├── sample-project/   # Sample application
    └── demo-scripts/     # Demo automation
```

## Configuration

### Basic Configuration

```yaml
# opendevin.yaml
agent:
  type: CodeActAgent
  model: claude-3-opus
  
sandbox:
  type: docker
  image: python:3.11-slim
  
testing:
  framework: pytest
  coverage_threshold: 80
```

### Environment Variables

```bash
export OPENDEVIN_MODEL=claude-3-opus
export OPENDEVIN_SANDBOX_TYPE=docker
export OPENDEVIN_COVERAGE_THRESHOLD=80
```

## API Reference

### OpenDevinAgent

```python
from openclaw.integrations.opendevin import OpenDevinAgent

agent = OpenDevinAgent()

# Generate code
result = agent.generate(
    spec="Create a REST API",
    language="python",
    framework="fastapi"
)

# Run tests
test_result = agent.test(path="./tests")

# Refactor code
refactor_result = agent.refactor(
    path="./src",
    goal="improve performance"
)

agent.close()
```

### TestAgent

```python
from openclaw.integrations.opendevin import TestAgent

agent = TestAgent()

# Generate tests
tests = agent.generate_tests(
    source_path="./src/main.py",
    framework="pytest"
)

# Run tests
result = agent.run_tests(
    test_path="./tests",
    coverage=True
)

agent.close()
```

### EnvironmentManager

```python
from openclaw.integrations.opendevin import EnvironmentManager

manager = EnvironmentManager()

# Create environment
env = manager.create(
    name="dev-env",
    template="python-fastapi"
)

# Execute commands
result = env.execute("pip install fastapi")

# Cleanup
env.destroy()
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

## License

This integration is part of OpenClaw and follows the main project license.

## Support

- Documentation: [OpenDevin Docs](https://github.com/OpenDevin/OpenDevin)
- Issues: [OpenClaw Issues](https://github.com/your-repo/openclaw/issues)
- Community: [Discord](https://discord.gg/openclaw)
