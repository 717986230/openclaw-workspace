# Contributing to OWL 🦉

Thank you for your interest in contributing to OWL (Omniverse Web Lab)!

OWL is a multi-agent collaboration framework built on [CAMEL-AI](https://github.com/camel-ai/camel), achieving **#1 on the GAIA benchmark** (69.09 avg score) and accepted to **NeurIPS 2025**. We welcome contributions from developers worldwide.

## Development Environment Setup

### Requirements
- Python 3.10 – 3.12
- Git
- Node.js 18+ (for web-related toolkits)
- Docker (optional, for containerized testing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/camel-ai/OWL.git
cd OWL

# Install dependencies
pip install -e .

# Or use uv for faster installs
uv sync

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable releases only |
| `develop` | Integration and testing |
| `feat/*` | Feature branches |
| `fix/*` | Bug fix branches |
| `docs/*` | Documentation improvements |

```bash
# Create a feature branch
git checkout -b feat/your-feature-name
git checkout -b fix/your-bug-description
```

## Code Style

We use standard Python tooling:

- **Formatting**: `ruff format` or `black`
- **Linting**: `ruff check`
- **Type checking**: `pyright` or `mypy`
- **Pre-commit**: Run `pre-commit install` after cloning

```bash
# Format and lint
ruff format .
ruff check .

# Type check
mypy owl/
```

All code should include type hints for better IDE support and maintainability.

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=owl --cov-report=html

# Run specific test file
pytest tests/agents/test_owla_agent.py -v
```

OWL uses **GAIA** (General AI Assistants) for agent evaluation:
```bash
python -m owl.eval.run_gaia --dataset_path=<path>
```

## AI-Generated Code Policy

> ⚠️ **Important**: The CAMEL-AI organization requires disclosure when submitting AI-generated code.

If your contribution contains AI-generated content:
1. Clearly state in your PR description which parts were AI-generated
2. You are responsible for ensuring the code is correct and tested
3. AI-generated code must meet the same quality standards as human-written code

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows the style guidelines (`ruff format && ruff check`)
- [ ] Type hints are added for all new functions/classes
- [ ] Tests are added or updated for new functionality
- [ ] Documentation is updated if needed
- [ ] `CONTRIBUTING.md` is referenced if contributing for the first time
- [ ] If AI-generated code is included, it is disclosed in the PR description
- [ ] All existing tests pass
- [ ] Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat: add new toolkit`
  - `fix: handle timeout in browser toolkit`
  - `docs: update README`
  - `test: add coverage for researcher agent`

### Submitting Your PR

1. **Fork** the repository
2. **Create** a feature branch from `develop`
3. **Make** your changes
4. **Push** to your fork
5. **Open** a Pull Request targeting `develop` on `camel-ai/OWL`

PR title format: `type(scope): description`

### Review Process

- PRs require at least **1 approval** from a maintainer
- Address reviewer feedback by pushing new commits
- Once approved, a maintainer will merge your PR

## Issue Templates

Before opening an issue, please check:
- [Existing issues](https://github.com/camel-ai/OWL/issues) to avoid duplicates
- [Closed issues](https://github.com/camel-ai/OWL/issues?q=is%3Aissue+is%3Aclosed) for similar problems

We welcome:
- 🐛 Bug reports with minimal reproduction steps
- 💡 Feature requests with clear use cases
- 📖 Documentation improvements
- 🔧 Toolkit contributions (Browser, Terminal, File, Excel, etc.)

## Community

Join the CAMEL-AI community:

| Platform | Link |
|----------|------|
| Discord | [discord.camel-ai.org](https://discord.camel-ai.org) |
| X (Twitter) | [@camel_ai_org](https://x.com/camel_ai_org) |
| Reddit | [r/CAMEL_AI](https://reddit.com/r/CAMEL_AI) |
| WeChat | See README for QR code |
| GitHub Discussions | [Discussions](https://github.com/camel-ai/OWL/discussions) |

## License

By contributing to OWL, you agree that your contributions will be licensed under the **Apache 2.0 License**.

---

**Happy contributing!** 🦉

*OWL: Omniverse Web Lab — Where agents collaborate to solve complex tasks.*