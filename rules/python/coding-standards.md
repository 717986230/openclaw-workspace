# Python Coding Standards

This document defines the coding standards for Python projects in the OpenClaw workspace. These rules supplement the common coding style rules.

## Code Style

-   **PEP 8:** Follow PEP 8 style guide for Python code.
-   **Type Hints:** Use type hints for function signatures and complex types.
-   **Docstrings:** Use docstrings for all modules, classes, and public functions.
-   **Naming Conventions:** Use `snake_case` for variables and functions, `PascalCase` for classes.

## Best Practices

-   **Error Handling:** Use specific exceptions and handle errors gracefully.
-   **Resource Management:** Use context managers (`with` statements) for resource management.
-   **Imports:** Group imports into standard library, third-party, and local imports.
-   **Testing:** Write unit tests for all critical functionality.

## Security

-   **Input Validation:** Validate all user inputs and external data.
-   **SQL Injection:** Use parameterized queries to prevent SQL injection.
-   **Secrets:** Do not hardcode secrets or credentials in code.

## Performance

-   **Optimization:** Optimize code for readability first, performance second.
-   **Profiling:** Profile code before optimizing to identify bottlenecks.
-   **Caching:** Use caching for expensive operations.

## Dependencies

-   **Requirements:** Maintain a `requirements.txt` or `pyproject.toml` file.
-   **Virtual Environments:** Use virtual environments for dependency isolation.
-   **Version Pinning:** Pin dependency versions for reproducibility.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
