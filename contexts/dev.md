# Development Context

This context is used when the agent is in development mode. It provides guidelines and preferences for development tasks.

## Development Guidelines

- **Code Quality:** Follow the coding standards defined in `rules/`.
- **Testing:** Write tests for all new features and bug fixes.
- **Documentation:** Update documentation when making changes.
- **Review:** Use code review tools to ensure quality.

## Development Preferences

- **Language:** Python and TypeScript are preferred for new projects.
- **Tools:** Use the local AI delegation tools for complex tasks.
- **Workflow:** Follow the standard workflow: acknowledge, plan, implement, verify.

## Development Environment

- **Workspace:** `C:\Users\Administrator\.openclaw\workspace`
- **Database:** `memory/database/xiaozhi_memory.db`
- **Logs:** `logs/`
- **State:** `state/`

## Development Commands

- **Check Status:** `openclaw status`
- **Run Tests:** `pytest tests/`
- **Lint Code:** `eslint .` or `flake8 .`
- **Format Code:** `prettier --write .` or `black .`

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
