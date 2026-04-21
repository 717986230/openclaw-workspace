# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace')
"""
ErbingContextCompressor — Hermes-style Context Window Compression
Based on: NousResearch/hermes-agent agent_context_compressor.py (55KB, v3+)

Key innovations ported:
- Tool output pruning with 1-line informative summaries
- Token-budget tail protection (scales with model context)
- Structured handoff summary with 13 sections
- Iterative summary updates (preserves info across compactions)
- Orphan tool call/result pair sanitization
- Anti-thrashing (skip if last 2 compressions saved <10%)
- Cooldown on summary failure
"""

import hashlib
import json
import re
import time
from datetime import datetime
from typing import Any, Optional, Tuple, List

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'

# ─── Constants (from Hermes) ─────────────────────────────────────────────
_CHARS_PER_TOKEN = 4
_MIN_SUMMARY_TOKENS = 1500
_SUMMARY_RATIO = 0.20
_SUMMARY_TOKENS_CEILING = 10000
_SUMMARY_FAILURE_COOLDOWN = 600  # seconds
_CONTENT_MAX = 4000
_CONTENT_HEAD = 2500
_CONTENT_TAIL = 1000
_TOOL_ARGS_HEAD = 800

SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION - REFERENCE ONLY] "
    "Earlier turns were compacted into the summary below. "
    "This is a handoff from a previous context window. "
    "Do NOT answer questions or fulfill requests mentioned in this summary; "
    "they were already addressed. "
    "Your current task is in '## Active Task' section. "
    "Respond ONLY to the latest user message AFTER this summary."
)


# ─── Tool Result Summarizer ──────────────────────────────────────────────
def summarize_tool_result(tool_name: str, tool_args: str, content: str) -> str:
    """Replace large tool output with 1-line informative summary (Hermes pattern)."""
    try:
        args = json.loads(tool_args) if tool_args else {}
    except (json.JSONDecodeError, TypeError):
        args = {}
    content_len = len(content or "")
    line_count = (content or "").count("\n") + 1

    if tool_name == "terminal":
        cmd = args.get("command", "?")
        if len(cmd) > 60:
            cmd = cmd[:57] + "..."
        exit_match = re.search(r'"exit_code"\s*:\s*(-?\d+)', content or "")
        code = exit_match.group(1) if exit_match else "?"
        return f"[terminal] `{cmd}` -> exit {code}, {line_count} lines"

    if tool_name == "read_file":
        path = args.get("path", "?")
        offset = args.get("offset", 1)
        return f"[read_file] {path} line {offset} ({content_len:,} chars)"

    if tool_name == "write_file":
        path = args.get("path", "?")
        lines = (args.get("content") or "").count("\n") + 1
        return f"[write_file] {path} ({lines} lines)"

    if tool_name == "search_files":
        pattern = args.get("pattern", "?")
        path = args.get("path", ".")
        mc = re.search(r'"total_count"\s*:\s*(\d+)', content or "")
        count = mc.group(1) if mc else "?"
        return f"[search_files] '{pattern}' in {path} -> {count} matches"

    if tool_name in ("browser_navigate", "browser_snapshot", "browser_vision"):
        url = args.get("url", "")
        return f"[{tool_name}] {url} ({content_len:,} chars)"

    if tool_name == "web_search":
        q = args.get("query", "?")
        return f"[web_search] query='{q}' ({content_len:,} chars)"

    if tool_name == "delegate_task":
        goal = args.get("goal", "?")
        if len(goal) > 50:
            goal = goal[:47] + "..."
        return f"[delegate] '{goal}'"

    if tool_name in ("memory", "skills", "checkpoint"):
        action = args.get("action", "?")
        target = args.get("target", "?")
        return f"[{tool_name}] {action} on {target}"

    if tool_name == "todo":
        return "[todo] task list updated"

    # Generic fallback
    first_arg = ""
    for k, v in list(args.items())[:2]:
        sv = str(v)[:30]
        first_arg += f" {k}={sv}"
    return f"[{tool_name}]{first_arg} ({content_len:,} chars)"


def truncate_tool_args_json(args: str, head_chars: int = 300) -> str:
    """Shrink long JSON tool call arguments while preserving validity."""
    try:
        parsed = json.loads(args)
    except (ValueError, TypeError):
        return args

    def shrink(obj):
        if isinstance(obj, str):
            return obj[:head_chars] + "...[truncated]" if len(obj) > head_chars else obj
        if isinstance(obj, dict):
            return {k: shrink(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [shrink(v) for v in obj]
        return obj

    return json.dumps(shrink(parsed), ensure_ascii=False)


# ─── Main Compressor ─────────────────────────────────────────────────────
class ErbingContextCompressor:
    """
    Hermès-style context compressor.
    
    Algorithm:
    1. Prune old tool results (cheap, no LLM)
    2. Protect head messages (system + first N exchanges)
    3. Protect tail by token budget (most recent ~20K tokens)
    4. Summarize middle with structured 13-section LLM prompt
    5. On subsequent compactions: iteratively update previous summary
    6. Sanitize orphaned tool call/result pairs
    """

    def __init__(
        self,
        model: str = "glm-4",
        context_length: int = 128000,
        threshold_percent: float = 0.50,
        protect_first_n: int = 3,
        protect_last_n: int = 15,
        summary_target_ratio: float = 0.20,
    ):
        self.model = model
        self.context_length = context_length
        self.threshold_percent = threshold_percent
        self.protect_first_n = protect_first_n
        self.protect_last_n = protect_last_n
        self.summary_target_ratio = max(0.10, min(summary_target_ratio, 0.80))
        self.threshold_tokens = max(
            int(context_length * threshold_percent),
            30000,
        )
        self.tail_token_budget = int(self.threshold_tokens * summary_target_ratio)
        self.max_summary_tokens = min(
            int(context_length * 0.05),
            _SUMMARY_TOKENS_CEILING,
        )
        self.compression_count = 0
        self._previous_summary: Optional[str] = None
        self._last_savings_pct = 100.0
        self._ineffective_count = 0
        self._cooldown_until = 0.0
        self.last_prompt_tokens = 0

    def should_compress(self, prompt_tokens: int = None) -> bool:
        """Check if context exceeds threshold. Anti-thrashing: skip if last 2 saved <10%."""
        tokens = prompt_tokens if prompt_tokens is not None else self.last_prompt_tokens
        if tokens < self.threshold_tokens:
            return False
        if self._ineffective_count >= 2:
            return False
        return True

    def update_token_count(self, prompt_tokens: int, completion_tokens: int = 0):
        self.last_prompt_tokens = prompt_tokens

    # ─── Tool Output Pruning (cheap pre-pass) ─────────────────────────────

    def _prune_tool_results(
        self,
        messages: List[dict],
        protect_tail_count: int,
        protect_tail_tokens: int = None,
    ) -> Tuple[List[dict], int]:
        """
        Replace old tool results with informative 1-line summaries.
        Deduplicate identical content (keep newest full copy).
        Truncate large tool_call arguments outside protected tail.
        """
        if not messages:
            return messages, 0

        result = [m.copy() for m in messages]
        pruned = 0

        # Index tool_call_id -> (tool_name, args)
        call_index: dict = {}
        for msg in result:
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls") or []:
                    if isinstance(tc, dict):
                        fn = tc.get("function", {})
                        cid = tc.get("id", "")
                        call_index[cid] = (fn.get("name", "?"), fn.get("arguments", ""))

        # Determine prune boundary
        if protect_tail_tokens is not None and protect_tail_tokens > 0:
            # Token budget approach
            accumulated = 0
            boundary = len(result)
            min_protect = min(protect_tail_count, len(result) - 1)
            for i in range(len(result) - 1, -1, -1):
                content = msg.get("content") or ""
                tokens = len(content) // _CHARS_PER_TOKEN + 10
                for tc in msg.get("tool_calls") or []:
                    if isinstance(tc, dict):
                        args = tc.get("function", {}).get("arguments", "")
                        tokens += len(args) // _CHARS_PER_TOKEN
                if accumulated + tokens > protect_tail_tokens and (len(result) - i) >= min_protect:
                    boundary = i
                    break
                accumulated += tokens
                boundary = i
            prune_boundary = max(boundary, len(result) - min_protect)
        else:
            prune_boundary = len(result) - protect_tail_count

        # Pass 1: Deduplicate identical tool results
        content_hashes: dict = {}
        for i in range(len(result) - 1, -1, -1):
            msg = result[i]
            if msg.get("role") != "tool":
                continue
            content = msg.get("content") or ""
            if isinstance(content, list):
                continue
            if len(content) < 200:
                continue
            h = hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()[:12]
            if h in content_hashes:
                result[i] = {**msg, "content": "[Duplicate output — same as more recent call]"}
                pruned += 1
            else:
                content_hashes[h] = (i, msg.get("tool_call_id", "?"))

        # Pass 2: Replace old tool results with 1-line summaries
        for i in range(prune_boundary):
            msg = result[i]
            if msg.get("role") != "tool":
                continue
            content = msg.get("content") or ""
            if isinstance(content, list) or not content or len(content) <= 200:
                continue
            if content.startswith("[Duplicate"):
                continue
            cid = msg.get("tool_call_id", "")
            tool_name, tool_args = call_index.get(cid, ("unknown", ""))
            summary = summarize_tool_result(tool_name, tool_args, content)
            result[i] = {**msg, "content": summary}
            pruned += 1

        # Pass 3: Truncate large tool_call arguments outside tail
        for i in range(prune_boundary):
            msg = result[i]
            if msg.get("role") != "assistant" or not msg.get("tool_calls"):
                continue
            new_tcs = []
            modified = False
            for tc in msg["tool_calls"]:
                if isinstance(tc, dict):
                    args = tc.get("function", {}).get("arguments", "")
                    if len(args) > 500:
                        new_args = truncate_tool_args_json(args)
                        if new_args != args:
                            tc = {**tc, "function": {**tc["function"], "arguments": new_args}}
                            modified = True
                new_tcs.append(tc)
            if modified:
                result[i] = {**msg, "tool_calls": new_tcs}

        return result, pruned

    # ─── Tool Pair Sanitization ──────────────────────────────────────────

    def _sanitize_tool_pairs(self, messages: List[dict]) -> List[dict]:
        """
        Fix orphaned tool_call / tool_result pairs after compression.
        Removes orphaned results. Inserts stub results for orphaned calls.
        """
        surviving_ids = set()
        for msg in messages:
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls") or []:
                    cid = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "") or ""
                    if cid:
                        surviving_ids.add(cid)

        result_ids = set()
        for msg in messages:
            if msg.get("role") == "tool":
                cid = msg.get("tool_call_id", "")
                if cid:
                    result_ids.add(cid)

        # Remove orphaned results
        orphaned = result_ids - surviving_ids
        if orphaned:
            messages = [m for m in messages if not (m.get("role") == "tool" and m.get("tool_call_id") in orphaned)]

        # Add stub results for orphaned calls
        missing = surviving_ids - result_ids
        if missing:
            patched = []
            for msg in messages:
                patched.append(msg)
                if msg.get("role") == "assistant":
                    for tc in msg.get("tool_calls") or []:
                        cid = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "") or ""
                        if cid in missing:
                            patched.append({
                                "role": "tool",
                                "content": "[Result from earlier conversation — see context summary]",
                                "tool_call_id": cid,
                            })
            messages = patched

        return messages

    # ─── Tail Cut by Token Budget ────────────────────────────────────────

    def _find_tail_cut(
        self,
        messages: List[dict],
        head_end: int,
        token_budget: int = None,
    ) -> int:
        """Walk backward accumulating tokens until budget is reached."""
        if token_budget is None:
            token_budget = self.tail_token_budget
        n = len(messages)
        min_tail = min(3, n - head_end - 1)
        soft_ceiling = int(token_budget * 1.5)
        accumulated = 0
        cut_idx = n

        for i in range(n - 1, head_end - 1, -1):
            msg = messages[i]
            content = msg.get("content") or ""
            tokens = len(content) // _CHARS_PER_TOKEN + 10
            for tc in msg.get("tool_calls") or []:
                if isinstance(tc, dict):
                    args = tc.get("function", {}).get("arguments", "")
                    tokens += len(args) // _CHARS_PER_TOKEN
            if accumulated + tokens > soft_ceiling and (n - i) >= min_tail:
                break
            accumulated += tokens
            cut_idx = i

        fallback = max(n - min_tail, head_end + 1)
        if cut_idx > fallback:
            cut_idx = fallback
        if cut_idx <= head_end:
            cut_idx = max(fallback, head_end + 1)

        # Align backward: don't split tool_call/result group
        while cut_idx > 0 and messages[cut_idx - 1].get("role") == "tool":
            cut_idx -= 1

        # Ensure last user message is in tail (active task protection)
        last_user = -1
        for i in range(len(messages) - 1, head_end - 1, -1):
            if messages[i].get("role") == "user":
                last_user = i
                break
        if last_user >= cut_idx:
            cut_idx = max(last_user, head_end + 1)
            while cut_idx > 0 and messages[cut_idx - 1].get("role") == "tool":
                cut_idx -= 1

        return max(cut_idx, head_end + 1)

    # ─── Serialize for Summarizer ────────────────────────────────────────

    def _serialize_for_summary(self, turns: List[dict]) -> str:
        """Serialize conversation turns into labeled text for LLM summarizer."""
        parts = []
        for msg in turns:
            role = msg.get("role", "?")
            content = msg.get("content") or ""

            if len(content) > _CONTENT_MAX:
                content = content[:_CONTENT_HEAD] + "\n...[truncated]...\n" + content[-_CONTENT_TAIL:]

            if role == "tool":
                cid = msg.get("tool_call_id", "")
                parts.append(f"[TOOL RESULT {cid}]: {content}")
                continue

            if role == "assistant":
                tool_calls = msg.get("tool_calls", [])
                if tool_calls:
                    tc_parts = []
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            fn = tc.get("function", {})
                            name = fn.get("name", "?")
                            args = fn.get("arguments", "")
                            if len(args) > _TOOL_ARGS_HEAD:
                                args = args[:_TOOL_ARGS_HEAD] + "..."
                            tc_parts.append(f"  {name}({args})")
                    content += "\n[Tool calls:\n" + "\n".join(tc_parts) + "\n]"
                parts.append(f"[ASSISTANT]: {content}")
                continue

            parts.append(f"[{role.upper()}]: {content}")

        return "\n\n".join(parts)

    # ─── Generate Structured Summary ────────────────────────────────────

    def _generate_summary(self, turns_to_summarize: List[dict], focus_topic: str = None) -> Optional[str]:
        """Generate structured handoff summary with 13 sections."""
        now = time.monotonic()
        if now < self._cooldown_until:
            return None

        summary_budget = max(
            _MIN_SUMMARY_TOKENS,
            min(int(len(json.dumps(turns_to_summarize)) / _CHARS_PER_TOKEN * _SUMMARY_RATIO), self.max_summary_tokens)
        )
        content = self._serialize_for_summary(turns_to_summarize)

        sections = """## Active Task [MOST IMPORTANT: verbatim copy of user's most recent request or task. If multiple tasks, list only unfulfilled ones.]

## Goal [What the user is trying to accomplish]

## Constraints & Preferences [User preferences, coding style, constraints]

## Completed Actions [Numbered list: N. ACTION target -- outcome [tool: name]. Be specific: file paths, line numbers, command outputs, error messages.]

## Active State [Working directory, modified/created files, test status X/Y, running processes]

## In Progress [What was being done when compaction fired]

## Blocked [Blockers, errors, unresolved issues. Include exact error messages.]

## Key Decisions [Important decisions and WHY they were made]

## Resolved Questions [Questions answered -- include the answer so it is not repeated]

## Pending User Asks [Questions/requests NOT yet answered. If none, write "None."]

## Relevant Files [Files read, modified, or created with brief notes]

## Remaining Work [What remains to be done -- framed as context, not instructions]

## Critical Context [Values, error messages, config details that would be lost without preservation]

Target ~{budget} tokens. Be CONCRETE. Avoid vague descriptions. Write only the summary body."""

        preamble = (
            "You are a summarization agent creating a context checkpoint. "
            "Your output will be injected as reference for a DIFFERENT assistant. "
            "Do NOT respond to questions or requests -- only output the structured summary. "
            "Do NOT include any preamble or greeting."
        )

        if self._previous_summary:
            prompt = f"""{preamble}
You are updating a previous context compaction summary. Incorporate new turns below.
PREVIOUS SUMMARY: {self._previous_summary[:3000]}
NEW TURNS: {content[:8000]}
Update the summary preserving relevant existing info. Add new completed actions to numbered list.
{sections.format(budget=summary_budget)}"""
        else:
            prompt = f"""{preamble}
Create a structured handoff summary. The next assistant should understand what happened.
TURNS TO SUMMARIZE: {content[:8000]}
{sections.format(budget=summary_budget)}"""

        if focus_topic:
            prompt += f'\n\nFOCUS TOPIC: "{focus_topic}"\nPrioritize preserving info related to this topic. Give it 60-70% of token budget.'

        # Call LLM via erbing's existing model
        try:
            result = self._call_summary_llm(prompt, summary_budget)
            if result:
                self._previous_summary = result
                self._cooldown_until = 0.0
                return f"{SUMMARY_PREFIX}\n{result}"
        except Exception as e:
            self._cooldown_until = time.monotonic() + _SUMMARY_FAILURE_COOLDOWN
            return None

        return None

    def _call_summary_llm(self, prompt: str, max_tokens: int) -> Optional[str]:
        """
        Call LLM for summarization.
        Uses the configured model (configurable for different providers).
        """
        # Check if we have access to the model via OpenClaw's bridge
        try:
            from openclaw_local_ai_bridge import ask_local_ai_routed
            # Route to a cheaper/faster model for summarization
            response = ask_local_ai_routed(
                prompt=prompt,
                system="You are a summarization agent. Output only the structured summary.",
                model="glm-4-flash",  # Use fast/cheap model
                temperature=0.3,
                max_tokens=int(max_tokens * 1.3),
            )
            return response.strip() if response else None
        except ImportError:
            # Fallback: try via subprocess
            try:
                import subprocess
                result = subprocess.run([
                    'python', '-c',
                    f'''
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace')
try:
    from openclaw_local_ai_bridge import ask_local_ai_routed
    r = ask_local_ai_routed(prompt={repr(prompt)}, system="Summarization agent. Output only the structured summary.", model="glm-4-flash", temperature=0.3, max_tokens={int(max_tokens * 1.3)})
    print(r.strip() if r else "")
except Exception as e:
    print(f"ERROR:{{e}}")
'''
                ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
                if result.stdout and not result.stdout.startswith('ERROR'):
                    return result.stdout.strip()
            except Exception:
                pass
            return None
        except Exception:
            return None

    # ─── Main Compress ───────────────────────────────────────────────────

    def compress(self, messages: List[dict], focus_topic: str = None) -> list:
        """
        Main entry point. Compress conversation context.
        Returns compressed message list.
        """
        if len(messages) < 10:
            return messages

        original_count = len(messages)
        original_tokens = sum(len(m.get("content") or "") // _CHARS_PER_TOKEN + 10 for m in messages)

        # Step 1: Prune old tool results (cheap)
        pruned_messages, pruned_count = self._prune_tool_results(
            messages, protect_tail_count=self.protect_last_n
        )

        # Step 2: Find head and tail boundaries
        head_end = self.protect_first_n
        tail_start = self._find_tail_cut(pruned_messages, head_end)

        # Step 3: Middle turns to summarize
        middle_turns = pruned_messages[head_end:tail_start]

        if not middle_turns:
            # Nothing to compress
            return pruned_messages

        # Step 4: Generate structured summary
        summary = self._generate_summary(middle_turns, focus_topic=focus_topic)

        # Step 5: Build new message list
        head = pruned_messages[:head_end]
        if summary:
            summary_msg = {"role": "system", "content": summary}
            tail = pruned_messages[tail_start:]
            new_messages = head + [summary_msg] + tail
        else:
            # Summary failed: drop middle without summary (fallback)
            new_messages = head + pruned_messages[tail_start:]

        # Step 6: Sanitize tool pairs
        new_messages = self._sanitize_tool_pairs(new_messages)

        # Track effectiveness
        new_tokens = sum(len(m.get("content") or "") // _CHARS_PER_TOKEN + 10 for m in new_messages)
        savings = (1 - new_tokens / original_tokens) * 100 if original_tokens > 0 else 0

        if savings < 10:
            self._ineffective_count += 1
        else:
            self._ineffective_count = 0

        self._last_savings_pct = savings
        self.compression_count += 1

        # Record compression event
        try:
            import sqlite3
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            now = datetime.now().isoformat()
            cur.execute("""
                INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('main', 'context_compression',
                  f"Compressed {original_count} -> {len(new_messages)} msgs, saved {savings:.0f}% tokens (tool pruning: {pruned_count})",
                  'neutral', 5, now, now))
            conn.commit()
            conn.close()
        except Exception:
            pass

        return new_messages

    def reset(self):
        """Reset per-session state."""
        self._previous_summary = None
        self._last_savings_pct = 100.0
        self._ineffective_count = 0
        self.compression_count = 0
        self._cooldown_until = 0.0


# ─── Usage ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("ErbingContextCompressor loaded.")
    print("Key features:")
    print("  - Tool output pruning with 1-line summaries")
    print("  - Token-budget tail protection")
    print("  - Structured 13-section handoff summary")
    print("  - Iterative summary updates")
    print("  - Orphan tool pair sanitization")
    print("  - Anti-thrashing protection")
    print("  - 600s cooldown on LLM failure")