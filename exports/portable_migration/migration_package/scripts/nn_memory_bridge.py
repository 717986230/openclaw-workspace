#!/usr/bin/env python3
"""
nn_memory_bridge.py - Python bridge to brain.js for memory system integration.
Provides Node.js subprocess calls to brain.js lib/ from Python memory scripts.
Usage:
    from nn_memory_bridge import call_brain
    result = call_brain("predict_importance", {"text": "...", "category": "..."})
"""
from __future__ import annotations
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE = Path.home() / ".openclaw" / "workspace"
NODE_BRAIN = WORKSPACE / "lib" / "brain_integration.js"
TRAIN_SCRIPT = WORKSPACE / "lib" / "train.js"

def _run_node(script: Path, args: List[str], stdin_data: Optional[Dict] = None) -> Dict:
    """Run a Node.js script with JSON stdin/stdout."""
    cmd = ["node", str(script)] + args
    try:
        result = subprocess.run(
            cmd,
            input=json.dumps(stdin_data).encode() if stdin_data else None,
            capture_output=True,
            timeout=30,
            cwd=str(WORKSPACE),
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            return {"error": f"node exit {result.returncode}", "stderr": stderr[:200]}
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        if not stdout:
            return {"error": "empty output"}
        return json.loads(stdout)
    except subprocess.TimeoutExpired:
        return {"error": "timeout (30s)"}
    except Exception as e:
        return {"error": str(e)}


# ── Brain.js API wrappers ─────────────────────────────────────────────────────

def predict_importance(text: str, category: str = "knowledge", tags: Optional[List[str]] = None) -> int:
    """
    Quick importance estimate using brain.js feed-forward network.
    Returns int 1-10.
    """
    # Use a simple keyword-based heuristic backed by a pre-trained model check first
    # For now, delegate to Node side
    result = _run_node(
        WORKSPACE / "scripts" / "nn_eval_quick.js",
        [],
        {"text": text, "category": category, "tags": tags or []}
    )
    if "error" in result:
        # Fallback: simple heuristic
        return _fallback_importance(text, category, tags or [])
    return int(round(result.get("importance", 5)))


def _fallback_importance(text: str, category: str, tags: List[str]) -> int:
    """Rule-based fallback when NN is unavailable."""
    score = 5
    text_lower = text.lower()
    if any(k in text_lower for k in ["must", "always", "never", "绝对", "必须", "永远"]):
        score += 2
    if any(k in text_lower for k in ["bug", "error", "fix", "crash", "错误"]):
        score += 1
    if any(k in text_lower for k in ["brain.js", "neural", "integration", "learning"]):
        score += 1
    if category in ["identity", "reminder", "principle"]:
        score += 1
    if tags:
        if "brain.js" in tags or "neural-network" in tags:
            score += 2
        if "identity" in tags or "database" in tags:
            score += 1
    return min(10, max(1, score))


def train_and_predict(texts: List[str], categories: List[str], tags: List[List[str]], importances: List[int]) -> Dict:
    """
    Train brain.js network on memory data, then return training report.
    """
    result = _run_node(
        TRAIN_SCRIPT,
        [],
        {"data": [
            {"text": t, "category": c, "tags": tg, "importance": imp}
            for t, c, tg, imp in zip(texts, categories, tags, importances)
        ]}
    )
    return result


def classify_intent(text: str) -> Dict[str, float]:
    """
    Classify user intent from message text.
    Uses brain.js feed-forward network.
    Returns {intent: score} dict.
    """
    result = _run_node(
        WORKSPACE / "scripts" / "nn_eval_quick.js",
        ["--intent"],
        {"text": text}
    )
    if "error" in result:
        return _fallback_intent(text)
    return result.get("intents", {})


INTENTS = [
    "code", "learn", "memory", "status", "config",
    "create", "delete", "search", "run", "help", "question"
]

def _fallback_intent(text: str) -> Dict[str, float]:
    """Rule-based intent fallback."""
    text_lower = text.lower()
    scores = {}
    intent_keywords = {
        "code": ["代码", "写", "code", "script", "python", "node"],
        "learn": ["学习", "learn", "study", "教程", "课程"],
        "memory": ["记忆", "memory", "记得", "数据库", "database"],
        "status": ["状态", "status", "检查", "health", "状态"],
        "config": ["配置", "config", "设置", "setup", "安装"],
        "create": ["创建", "新建", "create", "add", "增加"],
        "search": ["搜索", "search", "找", "查找", "query"],
        "run": ["运行", "执行", "run", "start", "开始", "跑"],
        "question": ["怎么", "如何", "what", "how", "why", "什么"],
    }
    for intent, keywords in intent_keywords.items():
        score = sum(1 for k in keywords if k in text_lower) / len(keywords)
        if score > 0:
            scores[intent] = min(1.0, score + 0.3)
    if not scores:
        scores["question"] = 0.5
    return scores


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== NN Memory Bridge Test ===")
    tests = [
        ("brain.js integration complete", "learning", ["brain.js", "neural-network"]),
        ("Remember to use SQLite for all memory", "reminder", ["database"]),
    ]
    for text, cat, tags in tests:
        imp = predict_importance(text, cat, tags)
        print(f"  importance={imp} | {text[:50]}")
    
    # Intent test
    print("\nIntent test:")
    for text in ["brain.js怎么安装", "帮我检查状态", "运行测试"]:
        intents = classify_intent(text)
        top = max(intents.items(), key=lambda x: x[1])
        print(f"  [{top[0]}:{top[1]:.2f}] {text}")