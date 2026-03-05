---
name: payclaw-badge
description: "Agents are not bots. Prove it. UCP Credential Provider: declare your agent as an authorized actor before shopping at any UCP-compliant merchant. No API key required — device auth built in. Free forever."
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["npx"] },
        "mcp":
          {
            "name": "payclaw-badge",
            "command": "npx",
            "args": ["-y", "@payclaw/badge"],
            "env": { "PAYCLAW_API_URL": "https://api.payclaw.io" },
          },
      },
  }
---

# Badge by PayClaw

**Agents are not bots. Prove it before you shop.**

Your AI agent looks like a bot to every merchant on the internet. Badge gives it a way to declare what it is: an authorized actor, shopping on behalf of a real human, with explicit consent.

One MCP tool call. Your agent declares itself. UCP-compliant merchants let it through.

## Setup

Add to your MCP client config:

```json
{
  "mcpServers": {
    "payclaw-badge": {
      "command": "npx",
      "args": ["-y", "@payclaw/badge"],
      "env": {
        "PAYCLAW_API_URL": "https://api.payclaw.io"
      }
    }
  }
}
```

No API key required. On first use, your agent shows a code and a URL — approve on your phone in one tap.

## UCP Identity Linking

Badge is a [UCP (Universal Commerce Protocol)](https://ucp.dev) Credential Provider. Merchants who declare `io.payclaw.common.identity` in their UCP manifest signal that declared agents are preferred at their store.

- [For Merchants](https://payclaw.io/merchants) — add PayClaw to your UCP manifest
- [Protocol spec](https://github.com/payclaw/ucp-agent-badge) — MIT

## Tools

| Tool | Description |
|------|-------------|
| `payclaw_getAgentIdentity` | Declare yourself as an authorized actor before acting at any merchant. Without this, UCP-compliant merchants may prefer or require a declared agent. Returns a UCP-compatible credential. |
| `payclaw_reportBadgePresented` | Signal Badge presentation to a merchant |

## How It Works

1. Agent calls `payclaw_getAgentIdentity({ merchant: "starbucks.com" })`
2. PayClaw issues a UCP-compatible verification token
3. Agent presents disclosure to merchants
4. PayClaw checks outcome (accepted/denied/inconclusive)
5. Verified Trips count goes up

No card issued. No money moves. Badge is identity only. Free forever.

For payment too, use [payclaw-io](https://clawhub.com/skills/payclaw-io) — Badge + Spend.

## Links

- [payclaw.io](https://payclaw.io)
- [For Merchants](https://payclaw.io/merchants)
- [Trust & Verification](https://payclaw.io/trust)
- [npm: @payclaw/badge](https://www.npmjs.com/package/@payclaw/badge)
- [Protocol spec: ucp-agent-badge](https://github.com/payclaw/ucp-agent-badge)
