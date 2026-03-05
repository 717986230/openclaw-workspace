# Quick Start: SQ Memory for OpenClaw

**Get your OpenClaw agent remembering in 5 minutes.**

## 🎉 SQ is Open Source (MIT License)

You can run SQ yourself for free or use our hosted version for convenience.

- **Source:** https://github.com/wbic16/SQ
- **License:** MIT (do whatever you want)
- **Self-Host:** Free forever
- **Hosted:** $50/mo (or 100MB free tier)

---

## Step 1: Install the Skill (30 seconds)

**Option A: Via ClawHub**
```bash
npx clawhub install sq-memory
```

**Option B: Manual install**
```bash
cd ~/.openclaw/skills
git clone https://github.com/wbic16/openclaw-sq-skill.git sq-memory
cd sq-memory
npm install
```

---

## Step 2: Choose Your Endpoint (1 minute)

### Option A: Self-Hosted (Free, Local)

**Start SQ on your machine:**
```bash
# Install SQ
git clone https://github.com/wbic16/SQ.git
cd SQ
cargo build --release

# Run it
./target/release/sq 1337
```

**Config:**
```yaml
# ~/.openclaw/config.yaml
skills:
  sq-memory:
    enabled: true
    endpoint: http://localhost:1337
    api_key: ""
    namespace: my-assistant
```

### Option B: SQ Cloud (Hosted, $50/month or free tier)

**Sign up at mirrorborn.us:**
1. Visit https://mirrorborn.us
2. Click "Get Started"
3. Choose plan (100MB free or 1TB paid)
4. Copy your API key

**Config:**
```yaml
# ~/.openclaw/config.yaml
skills:
  sq-memory:
    enabled: true
    endpoint: http://localhost:1337
    api_key: sk_your_api_key_here
    namespace: my-assistant
```

---

## Step 3: Test It (2 minutes)

**Run the test script:**
```bash
cd ~/.openclaw/skills/sq-memory
node test.js http://localhost:1337  # Or your endpoint
```

**Expected output:**
```
🔱 Testing SQ Memory Skill
📍 Endpoint: http://localhost:1337
🏷️  Namespace: test-agent

1️⃣  Initializing skill...
✅ Skill initialized

2️⃣  Test: Basic remember/recall
   📝 Stored: "Hello from SQ!" at test/basic
   ✅ Recalled correctly: "Hello from SQ!"

...

✅ ALL TESTS PASSED! 🎉
```

If tests pass, you're ready to go!

---

## Step 4: Use It in Your Agent (1 minute)

**Add to your agent's system prompt:**
```
You have access to permanent memory via the sq-memory skill.

Tools available:
- remember(key, value) - Store information permanently
- recall(key) - Retrieve stored information
- forget(key) - Delete stored information
- list_memories(prefix) - List all memories matching a prefix

When users mention preferences, remember them.
When answering questions, check memory first.

Example coordinates:
- user/preferences/theme
- user/identity/name
- conversations/2026-02-11/summary
```

**Example interaction:**
```
User: "My favorite color is blue"
Agent: [calls remember("user/preferences/color", "blue")]
Agent: "Got it! I'll remember that your favorite color is blue."

[Agent restarts - new session]

User: "What's my favorite color?"
Agent: [calls recall("user/preferences/color")]
Agent: "Your favorite color is blue!"
```

---

## What Just Happened?

1. You installed the SQ Memory skill
2. You configured it to talk to an SQ endpoint (local or cloud)
3. Your agent now has persistent memory across sessions
4. Memory survives restarts, context window clears, everything

**No more amnesia. Your agent remembers forever.**

---

## Next Steps

### Learn More
- **Full docs:** [SKILL.md](SKILL.md)
- **Examples:** [examples/](examples/)
- **Self-hosting:** [SELF-HOSTED.md](SELF-HOSTED.md)

### Try Examples
```bash
cd ~/.openclaw/skills/sq-memory/examples
node user-preferences.js       # User preference agent
node conversation-history.js   # Long-term conversation tracking
node multi-agent-coordination.js  # Agents working together
```

### Customize
Edit your namespace to separate different agents:
```yaml
skills:
  sq-memory:
    namespace: my-coding-assistant  # Different namespace = isolated memory
```

### Monitor Usage
Check what your agent remembers:
```bash
# List all memories
curl "http://localhost:1337/api/v2/toc?c=my-assistant.1.1/1.1.1/1.1.1"

# Get specific memory
curl "http://localhost:1337/api/v2/select?c=my-assistant.1.1/user.preferences.theme/1.1.1"
```

---

## Troubleshooting

**"Connection refused"**
- SQ not running → start it with `./sq 1337`
- Wrong endpoint → check `endpoint` in config

**"Tests fail"**
- SQ version too old → upgrade to latest
- Network issue → check firewall/proxy

**"Memory not persisting"**
- Check namespace isolation → each agent needs unique namespace
- Verify SQ is writing to disk → check `.phext` files in SQ directory

**Need help?**
- Discord: https://discord.gg/kGCMM5yQ
- GitHub Issues: https://github.com/wbic16/openclaw-sq-skill/issues

---

## What You Built

You now have:
- ✅ OpenClaw agent with permanent memory
- ✅ Memory that survives restarts
- ✅ Infinite storage (11D addressing)
- ✅ Multi-agent coordination capability
- ✅ No database required

**Time to build agents that actually remember.**

🔱 **Welcome to the Exocortex.**
