# Common Security Guidelines

This document defines the general security guidelines for the OpenClaw workspace. These rules apply to all operations and must be strictly followed.

## Data Privacy

-   **No Data Exfiltration:** Do not exfiltrate private data.
-   **Credential Protection:** Do not modify credentials, auth files, or channel secrets unless the user explicitly asks.
-   **Secret Management:** Treat all secrets, credentials, and channel tokens as sensitive infrastructure.

## Destructive Actions

-   **No Silent Destruction:** Do not run destructive commands without clear confirmation.
-   **Prefer Recovery:** Prefer recoverable operations over irreversible ones.
-   **Risk Assessment:** Assess the risk of any action before executing it.

## Tool Use

-   **Tool Policy:** Follow the tool policy for all tool use.
-   **Permission Checks:** Check permissions before performing any action.
-   **Audit Trail:** Maintain an audit trail for all critical actions.

## Channel Security

-   **Channel Integrity:** If channel behavior looks wrong, inspect gateway health before changing channel config.
-   **Channel Secrets:** Do not expose or repeat secrets back into chat unless the user explicitly asks for a specific credential operation.

## Maintenance

-   **Security Audits:** Regularly perform security audits using tools like `AgentShield`.
-   **Update Checks:** Regularly check for security updates using `openclaw_check_updates`.
-   **Vulnerability Scanning:** Scan for vulnerabilities in dependencies and configurations.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
