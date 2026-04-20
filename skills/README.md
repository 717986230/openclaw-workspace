# OpenClaw Skills

This directory contains modular, reusable skills for the OpenClaw agent system. Each skill is a self-contained unit of knowledge and capability, designed to be triggered by specific contexts or user intents.

## What is a Skill?

A **Skill** is a specialized capability that the agent can invoke to perform a specific task. Unlike a generic script, a skill is:
- **Manifest-driven:** It has a `SKILL.md` file that defines its metadata.
- **Context-aware:** It knows when to activate based on triggers.
- **Self-documenting:** It includes descriptions, examples, and usage guidelines.

## Skill Structure

Each skill directory should contain at least a `SKILL.md` file:

```
skills/
└── my-skill/
    ├── SKILL.md          # Skill manifest and documentation
    ├── references/       # Optional: Reference materials
    └── scripts/          # Optional: Helper scripts
```

## SKILL.md Format

The `SKILL.md` file is the heart of a skill. It uses YAML frontmatter for metadata and Markdown for documentation.

### Example

```markdown
---
name: code-review
description: Comprehensive code review covering security, performance, and best practices.
triggers:
  - "review this code"
  - "check for vulnerabilities"
  - "code audit"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
capabilities:
  - security_analysis
  - performance_review
  - best_practices_check
---

# Code Review Skill

This skill performs a comprehensive review of code changes, focusing on security vulnerabilities, performance bottlenecks, and adherence to best practices.

## How It Works

1. **Security Analysis:** Scans for common security issues (SQL injection, XSS, etc.).
2. **Performance Review:** Identifies inefficient algorithms or resource usage.
3. **Best Practices:** Checks adherence to coding standards and patterns.

## Usage

Simply ask the agent to review code:
- "Review the changes in `src/main.ts`"
- "Check for security vulnerabilities in this PR"

## Examples

### Example 1: Security Review
**User:** "Review this code for security issues"
**Agent:** [Performs security analysis and reports findings]

### Example 2: Performance Review
**User:** "Check if this function is performant"
**Agent:** [Analyzes performance and suggests optimizations]
```

## Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | The unique identifier for the skill. |
| `description` | string | Yes | A brief description of what the skill does. |
| `triggers` | array | Yes | List of phrases or patterns that trigger this skill. |
| `dependencies` | array | No | List of tools or resources this skill requires. |
| `capabilities` | array | No | List of capabilities this skill provides. |

## Creating a New Skill

1. **Create a directory:** `mkdir skills/my-new-skill`
2. **Create SKILL.md:** Write the manifest and documentation.
3. **Test:** Verify the skill works as expected.
4. **Commit:** Add to version control.

## Best Practices

- **Be Specific:** Define clear triggers to avoid false positives.
- **Document Well:** Provide examples and usage guidelines.
- **Keep It Focused:** Each skill should do one thing well.
- **Use Dependencies:** Declare required tools to ensure availability.

## Examples of Good Skills

- `code-review`: Comprehensive code analysis
- `security-scan`: Vulnerability detection
- `memory-optimization`: Context and memory management
- `github-automation`: PR and issue automation

## Contributing

To contribute a new skill:
1. Follow the structure above.
2. Ensure the `SKILL.md` is complete and well-documented.
3. Test thoroughly before submitting.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
