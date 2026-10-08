#!/usr/bin/env python3
"""
NVIDIA Smart Model Router for OpenClaw
=======================================

Nothing here is hardcoded:

  - Model list  -> pulled live from NVIDIA's own /v1/models endpoint every run.
  - Health/speed -> measured from OpenClaw's real gateway.log (actual calls
                    that actually happened today), never assumed.
  - API keys     -> read out of ~/.openclaw/openclaw.json at runtime, never
                    embedded in this file (this repo is public on GitHub).

This exists because every "smart router" that ships with a fixed model
table rots the moment the provider renames/retires a model (this is exactly
what happened to kimi-k2.6 -> 404 and minimax-m2.7 -> 410 on 2026-09-08).
This router can't go stale that way: it asks NVIDIA what's alive right now,
and asks the gateway's own log what's actually been working right now.

Usage:
  nvidia_smart_router.py catalog                 # live models + observed health
  nvidia_smart_router.py route "<prompt>"        # recommend a model for this prompt
  nvidia_smart_router.py heal [--apply]          # check current primary/fallbacks
                                                  # against live health, print (or
                                                  # write) a repaired config
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path

OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
GATEWAY_LOG = Path.home() / "Library" / "Logs" / "openclaw" / "gateway.log"
HEALTH_CACHE = Path(__file__).resolve().parent.parent / "memory" / "model_health_cache.json"

# Task-complexity signal words. This is about *intent*, not models, so it
# doesn't rot the way a model-name table does - "design a system" means the
# same thing regardless of which model happens to be alive this month.
TIER_PATTERNS = {
    "cheap": [
        r"^(hi|hey|hello|thanks|thank you|ok|okay|got it|yes|no|nope|yep)\b",
        r"\b(list|show|cat|status|check if|what's in)\b",
        r"^\W{0,3}\w{1,12}\W{0,3}$",  # very short message
    ],
    "smart": [
        r"\b(design|architect|comprehensive|deep(ly)?|complex|trade-?off|root cause|audit|security review)\b",
    ],
    # everything else -> "balanced"
}


def load_config():
    return json.loads(OPENCLAW_CONFIG.read_text())


def nvidia_providers(config):
    """Every configured NVIDIA-compatible provider entry, whatever it's named."""
    providers = config.get("models", {}).get("providers", {})
    out = []
    for name, p in providers.items():
        if isinstance(p, dict) and p.get("apiKey") and p.get("baseUrl"):
            out.append((name, p["apiKey"], p["baseUrl"]))
    return out


def fetch_live_catalog(base_url, api_key, timeout=15):
    """Ask the provider what models exist right now. Source of truth #1."""
    req = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    return sorted(m["id"] for m in data.get("data", []) if isinstance(m, dict) and "id" in m)


LOG_LINE_RE = re.compile(
    r"^(?P<ts>\S+) .*\[model-fetch\] response provider=(?P<provider>\S+) "
    r"api=\S+ model=(?P<model>\S+) status=(?P<status>\d+) elapsedMs=(?P<elapsed>\d+)"
)


def parse_log_health(log_path=GATEWAY_LOG, max_lines=50000, window_hours=48):
    """Aggregate real success/failure/latency per model from what the gateway
    actually did. Source of truth #2 - this is the only thing that tells you
    a model is *currently* broken (404/410/429/timeout) vs currently fine.
    """
    stats = defaultdict(lambda: {"ok": 0, "fail": 0, "latencies_ms": [], "last_status": None, "last_seen": None})
    if not log_path.exists():
        return stats

    try:
        with open(log_path, errors="ignore") as f:
            lines = f.readlines()[-max_lines:]
    except OSError:
        return stats

    for line in lines:
        m = LOG_LINE_RE.match(line)
        if not m:
            continue
        model = m.group("model")
        status = int(m.group("status"))
        elapsed = int(m.group("elapsed"))
        s = stats[model]
        if 200 <= status < 300:
            s["ok"] += 1
            s["latencies_ms"].append(elapsed)
        else:
            s["fail"] += 1
        s["last_status"] = status
        s["last_seen"] = m.group("ts")
    return stats


def _match_health(model_id, health):
    """Log lines and catalog ids don't always match exactly (bare id vs
    vendor/id vs nvidia/vendor/id) - match tolerantly by suffix instead of
    hardcoding a mapping."""
    if model_id in health:
        return health[model_id]
    for k, v in health.items():
        if k.endswith("/" + model_id) or model_id.endswith("/" + k) or model_id.endswith(k) or k.endswith(model_id):
            return v
    return None


def score_catalog(catalog, health):
    """Rank live models by *observed* health. A model NVIDIA just published
    with zero observations yet is 'unknown', not excluded - it isn't
    penalized just for being new, but proven-healthy models are preferred."""
    scored = []
    for model_id in catalog:
        h = _match_health(model_id, health)
        if h is None or (h["ok"] + h["fail"]) == 0:
            scored.append({
                "model": model_id, "status": "unknown", "success_rate": None,
                "avg_latency_ms": None, "samples": 0, "last_status": None,
            })
            continue
        total = h["ok"] + h["fail"]
        rate = h["ok"] / total
        avg_lat = round(sum(h["latencies_ms"]) / len(h["latencies_ms"])) if h["latencies_ms"] else None
        status = "healthy" if rate >= 0.8 else ("degraded" if rate > 0 else "broken")
        scored.append({
            "model": model_id, "status": status, "success_rate": round(rate, 2),
            "avg_latency_ms": avg_lat, "samples": total, "last_status": h["last_status"],
        })

    def sort_key(e):
        rank = {"healthy": 0, "unknown": 1, "degraded": 2, "broken": 3}[e["status"]]
        latency = e["avg_latency_ms"] if e["avg_latency_ms"] is not None else 30_000
        return (rank, -(e["success_rate"] or 0), latency)

    return sorted(scored, key=sort_key)


def classify_tier(prompt):
    p = prompt.lower()
    for tier in ("cheap", "smart"):
        for pat in TIER_PATTERNS[tier]:
            if re.search(pat, p):
                return tier
    return "balanced"


def pick_for_tier(tier, ranked):
    """Pick a model for a tier from the live-ranked list. No model names are
    referenced - 'smart' prefers the biggest healthy model (parsed from
    size hints like 550b/120b/30b/8b that appear in ids), 'cheap' prefers
    the fastest healthy one, 'balanced' takes the best all-rounder."""
    usable = [e for e in ranked if e["status"] in ("healthy", "unknown")]
    if not usable:
        usable = ranked  # nothing healthy - degrade gracefully rather than error

    def param_size(entry):
        m = re.search(r"(\d+(?:\.\d+)?)\s*b\b", entry["model"].lower())
        return float(m.group(1)) if m else 0.0

    if tier == "cheap":
        timed = [e for e in usable if e["avg_latency_ms"] is not None]
        pool = timed or usable
        return min(pool, key=lambda e: e["avg_latency_ms"] or 0)
    if tier == "smart":
        return max(usable, key=param_size)
    known = [e for e in usable if e["success_rate"] is not None] or usable
    return known[0]


def build_fallback_chain(ranked, n=3):
    healthy = [e["model"] for e in ranked if e["status"] == "healthy"]
    unknown = [e["model"] for e in ranked if e["status"] == "unknown"]
    chain = (healthy + unknown)[:n]
    return chain


def cmd_catalog():
    config = load_config()
    providers = nvidia_providers(config)
    if not providers:
        print("No NVIDIA-compatible provider with apiKey+baseUrl found in openclaw.json", file=sys.stderr)
        sys.exit(1)
    name, key, base_url = providers[0]
    try:
        catalog = fetch_live_catalog(base_url, key)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"Could not reach {base_url}: {e}", file=sys.stderr)
        sys.exit(2)
    health = parse_log_health()
    ranked = score_catalog(catalog, health)
    print(json.dumps({"provider": name, "base_url": base_url, "models": ranked}, indent=2))


def cmd_route(prompt):
    config = load_config()
    providers = nvidia_providers(config)
    name, key, base_url = providers[0]
    catalog = fetch_live_catalog(base_url, key)
    health = parse_log_health()
    ranked = score_catalog(catalog, health)
    tier = classify_tier(prompt)
    choice = pick_for_tier(tier, ranked)
    print(json.dumps({"tier": tier, "recommended_model": choice["model"], "detail": choice}, indent=2))


def cmd_heal(apply_change):
    config = load_config()
    providers = nvidia_providers(config)
    name, key, base_url = providers[0]
    catalog = fetch_live_catalog(base_url, key)
    health = parse_log_health()
    ranked = score_catalog(catalog, health)

    defaults = config.get("agents", {}).get("defaults", {})
    current_primary = defaults.get("model", {}).get("primary")
    current_entry = next((e for e in ranked if current_primary and current_primary.endswith(e["model"])), None)

    report = {
        "current_primary": current_primary,
        "current_primary_status": current_entry["status"] if current_entry else "not-in-live-catalog",
        "top_healthy": [e["model"] for e in ranked if e["status"] == "healthy"][:5],
        "broken_in_current_config": [],
    }

    needs_repair = report["current_primary_status"] in ("broken", "not-in-live-catalog")
    for fb in defaults.get("model", {}).get("fallbacks", []):
        e = next((e for e in ranked if fb.endswith(e["model"])), None)
        if e and e["status"] == "broken":
            report["broken_in_current_config"].append(fb)

    provider_prefix = "nvidia/"  # matches how this openclaw config namespaces provider ids; not a model name
    new_chain = [provider_prefix + m for m in build_fallback_chain(ranked, n=3)]

    report["recommended_primary"] = new_chain[0] if new_chain else current_primary
    report["recommended_fallbacks"] = new_chain[1:] if len(new_chain) > 1 else []
    report["would_change"] = needs_repair or bool(report["broken_in_current_config"])

    if not apply_change:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if not report["would_change"]:
        print(json.dumps({"applied": False, "reason": "current config already healthy", **report}, indent=2, ensure_ascii=False))
        return

    import shutil
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = OPENCLAW_CONFIG.with_name(f"openclaw.json.bak-router-heal-{ts}")
    shutil.copy2(OPENCLAW_CONFIG, backup)

    defaults.setdefault("model", {})["primary"] = report["recommended_primary"]
    defaults["model"]["fallbacks"] = report["recommended_fallbacks"]
    config["agents"]["defaults"] = defaults
    OPENCLAW_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps({"applied": True, "backup": str(backup), **report}, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "catalog":
        cmd_catalog()
    elif cmd == "route":
        if len(sys.argv) < 3:
            print("Usage: nvidia_smart_router.py route \"<prompt>\"", file=sys.stderr)
            sys.exit(1)
        cmd_route(sys.argv[2])
    elif cmd == "heal":
        cmd_heal(apply_change="--apply" in sys.argv[2:])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
