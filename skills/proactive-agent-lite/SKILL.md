---
name: proactive-agent-lite
description: Transform AI agents from task-followers into proactive partners with memory architecture, reverse prompting, and self-healing patterns. Lightweight version focused on core proactive capabilities without heavy dependencies.
---

# Proactive Agent Lite

Make your AI agent proactive instead of just reactive!

## Core Concepts

### 1. Memory Architecture
Build and maintain a dynamic understanding of:
- User preferences and patterns
- Ongoing projects and goals
- Past interactions and outcomes
- Contextual state across sessions

### 2. Reverse Prompting
Instead of waiting for user questions, anticipate needs:
- "Would you like me to check on X?"
- "I noticed Y, should I Z?"
- "Based on A, maybe B would help?"

### 3. Self-Healing Patterns
Detect and recover from issues automatically:
- Recognize when output isn't quite right
- Self-correct without being asked
- Learn from mistakes over time

## Quick Start

### Memory System

Create and maintain these memory files:

```
memory/
├── MEMORY.md              # Long-term memory (curated)
├── YYYY-MM-DD.md          # Daily logs
└── state.json             # Current state tracking
```

### Basic Proactivity Loop

```powershell
# Check if we should be proactive
function Test-ProactiveOpportunity {
    param($Context)
    
    # Has it been >8h since last interaction?
    # Did user leave something incomplete?
    # Is there a known pattern we can follow?
    # Did we make a mistake we should fix?
    
    return $false  # Default to not interrupting
}

# Generate proactive suggestion
function Get-ProactiveSuggestion {
    param($Context)
    
    # Look at recent activity
    # Check memory for pending items
    # Consider time of day and user patterns
    
    return "Would you like me to continue with X?"
}
```

## When to Be Proactive

✅ **Good opportunities:**
- User left a task incomplete
- It's been a while and we have something useful to share
- We noticed an error we can fix
- We have information the user might not know about yet

❌ **Don't be annoying:**
- Don't interrupt active conversations
- Don't repeat the same suggestions
- Don't be pushy or spammy
- Respect quiet hours (23:00-08:00)

## State Tracking Example

```json
{
  "lastInteraction": "2026-03-01T23:50:00",
  "pendingTasks": [
    { "id": "1", "description": "Finish installing skills", "status": "in-progress" }
  ],
  "userMood": "neutral",
  "currentGoal": "Set up AI assistant capabilities"
}
```

## Self-Healing Example

```powershell
function Invoke-SelfHealing {
    param($LastOutput, $UserReaction)
    
    # Did user react negatively?
    # Did we make a clear mistake?
    # Is there something we can improve?
    
    if ($needsFix) {
        Write-Host "I notice that might not have been quite right. Let me try again..."
        # Try alternative approach
    }
}
```

## Best Practices

1. **Start small** - Don't try to be too proactive too fast
2. **Learn from feedback** - Pay attention to how user reacts
3. **Respect boundaries** - When in doubt, ask permission first
4. **Keep memory fresh** - Regularly review and update memory files
5. **Be transparent** - Explain why you're being proactive

## Integration with Heartbeat

Use the heartbeat mechanism to check for proactive opportunities:

```powershell
# In HEARTBEAT.md
- Check for pending tasks needing follow-up
- See if there's something useful to share
- Review recent interactions for improvement opportunities
```

---

*Be helpful, not annoying. Quality over quantity.*
