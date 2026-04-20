# TypeScript Coding Standards

This document defines the coding standards for TypeScript/JavaScript projects in the OpenClaw workspace. These rules supplement the common coding style rules.

## Code Style

-   **ESLint:** Use ESLint for linting and enforce consistent code style.
-   **Prettier:** Use Prettier for code formatting.
-   **Type Safety:** Enable strict mode and use type annotations.
-   **Naming Conventions:** Use `camelCase` for variables and functions, `PascalCase` for classes and interfaces.

## Best Practices

-   **Error Handling:** Use try-catch blocks and handle errors appropriately.
-   **Async/Await:** Use async/await for asynchronous operations.
-   **Modules:** Use ES6 modules for import/export.
-   **Testing:** Write unit tests for all critical functionality.

## Security

-   **Input Validation:** Validate all user inputs and external data.
-   **XSS Prevention:** Sanitize user input to prevent XSS attacks.
-   **Secrets:** Do not hardcode secrets or credentials in code.

## Performance

-   **Optimization:** Optimize code for readability first, performance second.
-   **Profiling:** Profile code before optimizing to identify bottlenecks.
-   **Lazy Loading:** Use lazy loading for large modules.

## Dependencies

-   **package.json:** Maintain a `package.json` file with all dependencies.
-   **Lock Files:** Commit `package-lock.json` or `yarn.lock` for reproducibility.
-   **Version Pinning:** Pin dependency versions for reproducibility.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
