#!/usr/bin/env python3
"""SignalRadar v0.5.0 unified CLI entrypoint.

Commands: doctor, add, list, remove, run, config
Single source of truth: config/watchlist.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Resolve paths before importing sibling modules (they use relative imports)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from config_utils import (
    DEFAULT_CONFIG,
    add_entries,
    archive_entry,
    deep_merge,
    get_entry_by_number,
    load_json_config,
    load_watchlist,
    save_watchlist,
)
from decide_threshold import check_entry, safe_name
from discover_entries import (
    ONBOARDING_URLS,
    extract_probability,
    fetch_market_current,
    is_settled,
    normalize_market,
    parse_polymarket_url,
    resolve_event,
)
from route_delivery import deliver_hit, severity_for_event


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _workspace_root() -> Path:
    env = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env:
        return Path(env)
    return SKILL_ROOT.parent.parent


def _watchlist_path() -> Path:
    return SKILL_ROOT / "config" / "watchlist.json"


def _config_path(override: str = "") -> Path:
    if override:
        return Path(override)
    return SKILL_ROOT / "config" / "signalradar_config.json"


def _baseline_dir() -> Path:
    return SKILL_ROOT / "cache" / "baselines"


def _audit_log_path() -> Path:
    return SKILL_ROOT / "cache" / "events" / "signal_events.jsonl"


def _load_config(override: str = "") -> dict[str, Any]:
    user_cfg = load_json_config(_config_path(override))
    return deep_merge(DEFAULT_CONFIG, user_cfg)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# cmd_doctor
# ---------------------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    check("skill_root_exists", SKILL_ROOT.exists(), str(SKILL_ROOT))
    wl_path = _watchlist_path()
    if not wl_path.exists():
        check("watchlist_loadable", True, f"not yet created: {wl_path}")
    else:
        # Try strict JSON parse first to detect corruption
        try:
            raw = json.loads(wl_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                check("watchlist_loadable", False, f"watchlist is not a JSON object: {wl_path}")
            elif not isinstance(raw.get("entries"), list):
                check("watchlist_loadable", False, f"watchlist.entries missing or not a list: {wl_path}")
            elif not isinstance(raw.get("archived", []), list):
                check("watchlist_loadable", False, f"watchlist.archived is not a list: {wl_path}")
            else:
                check("watchlist_loadable", True, str(wl_path))
                check("watchlist_entries", True, f"{len(raw.get('entries', []))} entries")
        except (json.JSONDecodeError, ValueError) as e:
            check("watchlist_corrupted", False, f"JSON parse error: {e} — file: {wl_path}")

    cfg_path = _config_path(args.config)
    check("config_exists_optional", True, str(cfg_path) if cfg_path.exists() else f"missing(optional): {cfg_path}")
    cache_dir = SKILL_ROOT / "cache"
    check("cache_dir_writable", cache_dir.exists() or SKILL_ROOT.exists(), str(cache_dir))

    interval = config.get("check_interval_minutes", 10)
    ok = all(item["ok"] for item in checks)
    payload: dict[str, Any] = {
        "status": "HEALTHY" if ok else "WARN",
        "check_interval_minutes": interval,
        "checks": checks,
    }

    if args.output == "json":
        _json_print(payload)
    else:
        if ok:
            print(f"HEALTHY — check_interval_minutes={interval}")
        else:
            print("WARN")
            for item in checks:
                if not item["ok"]:
                    print(f"  - {item['name']}: {item['detail']}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# cmd_add
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> int:
    url = args.url
    slug = parse_polymarket_url(url)
    if not slug:
        print(f"Error: Cannot parse Polymarket event URL: {url}")
        return 1

    result = resolve_event(slug)
    if not result["ok"]:
        print(f"Error: {result['error']}")
        return 1

    event_title = result["event_title"]
    markets = result["markets"]
    event_id = result["event_id"]

    if not markets:
        print(f"No markets found for event '{event_title}'.")
        return 1

    # Check for settled markets
    settled_markets = [m for m in markets if is_settled(m)]
    active_markets = [m for m in markets if not is_settled(m)]

    if settled_markets and not active_markets:
        print(f"Warning: All {len(markets)} markets in '{event_title}' are settled.")
        if not args.yes:
            answer = input("Add anyway? (y/N): ").strip().lower()
            if answer not in ("y", "yes"):
                print("Cancelled.")
                return 0

    # Multi-market event: report count first, then confirm
    if len(active_markets) > 1:
        print(f"\n{event_title} — {len(active_markets)} markets found.", end="")
        if settled_markets:
            print(f" ({len(settled_markets)} settled, skipped.)", end="")
        print()

        if not args.yes:
            answer = input(f"Add all {len(active_markets)} markets? (Y/n): ").strip().lower()
            if answer in ("n", "no"):
                print("Cancelled.")
                return 0

    elif len(active_markets) == 1:
        m = active_markets[0]
        print(f"\n{m['question']}  {m['probability']:.0f}%")
        if not args.yes:
            answer = input("Add this market? (Y/n): ").strip().lower()
            if answer in ("n", "no"):
                print("Cancelled.")
                return 0
    else:
        # Only settled markets but user confirmed above
        active_markets = markets

    # Build watchlist entries
    category = args.category or "default"
    now = _utc_now()
    new_entries = []
    for m in active_markets:
        new_entries.append({
            "entry_id": m["entry_id"],
            "slug": m["slug"],
            "question": m["question"],
            "category": category,
            "url": m["url"],
            "end_date": m.get("end_date", ""),
            "added_at": now,
        })

    wl_path = _watchlist_path()
    added, skipped = add_entries(wl_path, new_entries)

    # Record baselines for newly added entries
    baseline_dir = _baseline_dir()
    for entry in added:
        # Find the market data to get probability
        for m in active_markets:
            if m["entry_id"] == entry["entry_id"]:
                check_entry(
                    entry_id=entry["entry_id"],
                    question=entry["question"],
                    current_prob=m["probability"],
                    baseline_dir=baseline_dir,
                    threshold_abs_pp=5.0,
                    dry_run=False,
                )
                break

    # Show results
    if added:
        print(f"\nAdded {len(added)} market(s):")
        for entry in added:
            prob = ""
            for m in active_markets:
                if m["entry_id"] == entry["entry_id"]:
                    prob = f"  {m['probability']:.0f}% (baseline)"
                    break
            print(f"  {entry['question']}{prob}")

    if skipped:
        print(f"\nSkipped {len(skipped)} (already in watchlist):")
        for entry in skipped:
            print(f"  {entry['question']}")

    # First-add frequency notice (only if this was the first addition)
    wl = load_watchlist(wl_path)
    if added and len(wl.get("entries", [])) == len(added):
        config = _load_config(args.config)
        interval = config.get("check_interval_minutes", 10)
        print(f"\nMonitoring frequency: every {interval} minutes (default).")
        print("To change: signalradar.py config check_interval_minutes 20")

    return 0


# ---------------------------------------------------------------------------
# cmd_config
# ---------------------------------------------------------------------------

def cmd_config(args: argparse.Namespace) -> int:
    cfg_path = _config_path(args.config)
    user_cfg = load_json_config(cfg_path)

    # No key specified: show current config
    if not args.key:
        merged = deep_merge(DEFAULT_CONFIG, user_cfg)
        if args.output == "json":
            _json_print(merged)
        else:
            print("Current config:\n")
            for k, v in sorted(merged.items()):
                if isinstance(v, dict):
                    print(f"  {k}:")
                    for k2, v2 in sorted(v.items()):
                        print(f"    {k2}: {v2}")
                else:
                    print(f"  {k}: {v}")
            print(f"\nConfig file: {cfg_path}")
        return 0

    key = args.key

    # No value specified: show current value for that key
    if args.value is None:
        merged = deep_merge(DEFAULT_CONFIG, user_cfg)
        if key in merged:
            print(f"{key}: {merged[key]}")
        else:
            print(f"Unknown key: {key}")
            return 1
        return 0

    # Set value
    raw_value = args.value
    # Auto-detect type: int, float, or string
    parsed_value: Any
    try:
        parsed_value = int(raw_value)
    except ValueError:
        try:
            parsed_value = float(raw_value)
        except ValueError:
            parsed_value = raw_value

    user_cfg[key] = parsed_value

    # Write config (atomic)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(
        json.dumps(user_cfg, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Set {key} = {parsed_value}")
    print(f"Saved to {cfg_path}")
    return 0


# ---------------------------------------------------------------------------
# cmd_list
# ---------------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())

    if args.archived:
        archived = wl.get("archived", [])
        if not archived:
            print("No archived entries.")
            return 0
        print(f"Archived entries ({len(archived)}):\n")
        for i, entry in enumerate(archived, 1):
            reason = entry.get("archive_reason", "unknown")
            archived_at = entry.get("archived_at", "")[:10]
            print(f"  {i}. {entry.get('question', entry.get('entry_id', '?'))}")
            print(f"     Reason: {reason}  Archived: {archived_at}")
        return 0

    entries = wl.get("entries", [])
    if not entries:
        print("Watchlist is empty. Use 'signalradar.py add <url>' to add markets.")
        return 0

    # Group by category
    by_category: dict[str, list[tuple[int, dict]]] = {}
    for i, entry in enumerate(entries, 1):
        cat = entry.get("category", "default")
        if args.category and cat != args.category:
            continue
        by_category.setdefault(cat, []).append((i, entry))

    if not by_category:
        print(f"No entries in category '{args.category}'.")
        return 0

    total = sum(len(v) for v in by_category.values())
    print(f"Watchlist ({total} entries):\n")
    for cat in sorted(by_category.keys()):
        print(f"  [{cat}]")
        for num, entry in by_category[cat]:
            q = entry.get("question", entry.get("entry_id", "?"))
            end = entry.get("end_date", "")
            print(f"    {num}. {q}" + (f"  (ends {end})" if end else ""))
        print()

    return 0


# ---------------------------------------------------------------------------
# cmd_remove
# ---------------------------------------------------------------------------

def cmd_remove(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entry = get_entry_by_number(wl, args.number)

    if entry is None:
        print(f"Error: No entry #{args.number}. Use 'signalradar.py list' to see entries.")
        return 1

    question = entry.get("question", entry.get("entry_id", "?"))
    print(f"\nRemoving #{args.number}: {question}")

    if not args.yes:
        answer = input("Confirm removal? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0

    # Collect baseline history before archiving
    entry_id = entry.get("entry_id", "")
    baseline_dir = _baseline_dir()
    baseline_file = baseline_dir / f"{safe_name(entry_id)}.json"
    baseline_history = []
    if baseline_file.exists():
        try:
            bl = json.loads(baseline_file.read_text(encoding="utf-8"))
            baseline_history.append({
                "value": bl.get("baseline"),
                "ts": bl.get("baseline_ts"),
            })
        except Exception:
            pass

    archived = archive_entry(
        _watchlist_path(),
        entry_id,
        reason="user_removed",
        baseline_history=baseline_history if baseline_history else None,
    )

    if archived:
        print(f"Archived: {question}")
    else:
        print("Error: Entry not found during archive.")
        return 1

    return 0


# ---------------------------------------------------------------------------
# cmd_run
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entries = wl.get("entries", [])
    config = _load_config(args.config)

    # Empty watchlist handling
    if not entries:
        if args.yes:
            # --yes mode: no onboarding, just report empty
            if args.output == "json":
                _json_print({
                    "status": "NO_REPLY",
                    "request_id": str(uuid.uuid4()),
                    "ts": _utc_now(),
                    "hits": [],
                    "errors": [],
                    "message": "Watchlist is empty",
                })
            else:
                print("Watchlist is empty. Use 'signalradar.py add <url>' to add markets.")
            return 0
        else:
            # Interactive mode: trigger onboarding
            return _onboarding(args)

    # Normal run: check each entry
    threshold_cfg = config.get("threshold", {})
    default_threshold = float(threshold_cfg.get("abs_pp", 5.0))
    per_entry_thresholds = threshold_cfg.get("per_entry_abs_pp", {})
    per_category_thresholds = threshold_cfg.get("per_category_abs_pp", {})

    baseline_dir = _baseline_dir()
    audit_log = _audit_log_path()

    request_id = str(uuid.uuid4())
    run_ts = _utc_now()
    hits: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    settled_entries: list[dict[str, Any]] = []
    checked = 0

    for entry in entries:
        entry_id = entry.get("entry_id", "")
        question = entry.get("question", "")
        category = entry.get("category", "default")

        # Fetch current market state
        market_id = entry_id.split(":")[1] if ":" in entry_id else ""
        if not market_id:
            errors.append({"entry_id": entry_id, "error": "invalid entry_id format"})
            continue

        current_market = fetch_market_current(market_id)
        if current_market is None:
            # API failure — check end_date as fallback for settled
            if is_settled(entry):
                settled_entries.append(entry)
                continue
            errors.append({"entry_id": entry_id, "error": "API fetch failed"})
            continue

        # Settled detection: API status priority
        if is_settled(current_market):
            settled_entries.append(entry)
            continue

        current_prob = current_market.get("probability")
        if current_prob is None:
            errors.append({"entry_id": entry_id, "error": "no probability data"})
            continue

        # Resolve threshold: per_entry > per_category > default
        threshold = default_threshold
        if entry_id in per_entry_thresholds:
            try:
                threshold = float(per_entry_thresholds[entry_id])
            except (TypeError, ValueError):
                pass
        elif category in per_category_thresholds:
            try:
                threshold = float(per_category_thresholds[category])
            except (TypeError, ValueError):
                pass

        result = check_entry(
            entry_id=entry_id,
            question=question,
            current_prob=current_prob,
            baseline_dir=baseline_dir,
            threshold_abs_pp=threshold,
            dry_run=args.dry_run,
            audit_log_path=audit_log,
        )
        checked += 1

        if result["decision"] == "HIT" and result["event"] is not None:
            hits.append(result["event"])
            # Deliver
            if not args.dry_run:
                deliver_hit(result["event"], config, dry_run=False)

    # Determine overall status
    if errors and not hits:
        status = "ERROR"
    elif hits:
        status = "HIT"
    else:
        status = "NO_REPLY"

    # Output
    if args.output == "json":
        payload: dict[str, Any] = {
            "status": status,
            "request_id": request_id,
            "ts": run_ts,
            "hits": hits,
            "errors": errors,
            "checked_count": checked,
            "settled_count": len(settled_entries),
        }
        _json_print(payload)
    else:
        if hits:
            print(f"HIT — {len(hits)} alert(s):\n")
            for h in hits:
                print(f"  {h.get('question', h.get('entry_id'))}")
                print(f"    {h.get('baseline')}% → {h.get('current')}%  ({h.get('abs_pp')}pp)")
                print(f"    Baseline updated to {h.get('current')}%")
                print()
        else:
            print(f"NO_REPLY — {checked} entries checked, no threshold crossings.")

        if errors:
            print(f"\n{len(errors)} error(s):")
            for e in errors:
                print(f"  {e.get('entry_id')}: {e.get('error')}")

        if settled_entries:
            print(f"\n{len(settled_entries)} entries settled, consider removing:")
            for e in settled_entries:
                print(f"  {e.get('question', e.get('entry_id', '?'))}")

    return 0 if status != "ERROR" else 1


# ---------------------------------------------------------------------------
# Onboarding: 3-step code-enforced flow
# ---------------------------------------------------------------------------

def _onboarding(args: argparse.Namespace) -> int:
    """First-time setup with 6 preset events. 3-step interactive flow."""

    print("Welcome to SignalRadar! Loading popular events...\n")

    # Resolve all preset URLs
    events_data: list[dict[str, Any]] = []
    for url in ONBOARDING_URLS:
        slug = parse_polymarket_url(url)
        if not slug:
            continue
        result = resolve_event(slug)
        if result["ok"]:
            markets = [m for m in result["markets"] if not is_settled(m)]
            events_data.append({
                "title": result["event_title"],
                "slug": result["slug"],
                "event_id": result["event_id"],
                "markets": markets,
                "url": url,
            })
        else:
            events_data.append({
                "title": slug.replace("-", " ").title(),
                "slug": slug,
                "event_id": "",
                "markets": [],
                "url": url,
                "unavailable": True,
            })

    if not events_data:
        print("Error: Could not load any preset events. Check network connection.")
        return 1

    # --- STEP 1: Show event titles + market counts ---
    print(f"Found {len(events_data)} events:\n")
    for i, ev in enumerate(events_data, 1):
        market_count = len(ev["markets"])
        unavail = " (unavailable)" if ev.get("unavailable") else ""
        suffix = f"({market_count} market{'s' if market_count != 1 else ''})"
        print(f"  {i}. {ev['title']}  {suffix}{unavail}")

    print()
    user_input = input("Enter numbers to REMOVE (e.g. 1,5), or press Enter to keep all: ").strip()

    # Parse removal choices
    remove_set: set[int] = set()
    if user_input:
        for part in user_input.replace(" ", ",").split(","):
            part = part.strip()
            if part.isdigit():
                remove_set.add(int(part))

    # Filter events
    kept_events = []
    for i, ev in enumerate(events_data, 1):
        if i not in remove_set and not ev.get("unavailable") and ev["markets"]:
            kept_events.append(ev)

    if not kept_events:
        print("\nNo events selected. You can add markets later with: signalradar.py add <url>")
        return 0

    # --- STEP 2: Show sub-market details, confirm ---
    total_markets = sum(len(ev["markets"]) for ev in kept_events)
    print(f"\nAdding {len(kept_events)} events ({total_markets} markets):\n")

    # Group by inferred category
    num = 0
    for ev in kept_events:
        for m in ev["markets"]:
            num += 1
            print(f"  {num}. {m['question']}  {m['probability']:.0f}%")
    print()

    answer = input(f"Confirm adding {total_markets} markets? (Y/n): ").strip().lower()
    if answer in ("n", "no"):
        print("Cancelled. You can add markets later with: signalradar.py add <url>")
        return 0

    # --- STEP 3: Add entries + show results ---
    now = _utc_now()
    wl_path = _watchlist_path()
    baseline_dir = _baseline_dir()
    all_new_entries = []

    for ev in kept_events:
        category = _infer_category(ev["title"])
        for m in ev["markets"]:
            entry = {
                "entry_id": m["entry_id"],
                "slug": m["slug"],
                "question": m["question"],
                "category": category,
                "url": m["url"],
                "end_date": m.get("end_date", ""),
                "added_at": now,
            }
            all_new_entries.append((entry, m["probability"]))

    entries_to_add = [e for e, _ in all_new_entries]
    added, skipped = add_entries(wl_path, entries_to_add)

    # Record baselines
    for entry, prob in all_new_entries:
        if entry in added:
            check_entry(
                entry_id=entry["entry_id"],
                question=entry["question"],
                current_prob=prob,
                baseline_dir=baseline_dir,
                threshold_abs_pp=5.0,
                dry_run=False,
            )

    print(f"\nDone! {len(added)} markets added, baselines recorded.")
    if skipped:
        print(f"({len(skipped)} already in watchlist, skipped)")
    print("Remove any you don't need with: signalradar.py remove <number>")

    # Frequency notice
    config = _load_config(args.config)
    interval = config.get("check_interval_minutes", 10)
    print(f"\nMonitoring frequency: every {interval} minutes (default).")
    print("To change: signalradar.py config check_interval_minutes 20")
    print("Note: higher frequency = more API requests and more frequent alerts.")

    print(
        "\nWhat is a baseline?\n"
        "A baseline is the \"last known probability\" SignalRadar records. When probability\n"
        "changes by more than the threshold (default 5pp) and a notification is sent,\n"
        "the baseline updates to the new value. Example:\n"
        "  baseline 7% -> probability rises to 15% -> alert sent -> baseline updates to 15%\n"
        "  Next alert requires another 5pp change from 15%."
    )

    return 0


def _infer_category(title: str) -> str:
    """Simple keyword-based category for onboarding events."""
    lower = title.lower()
    ai_keywords = ["gpt", "claude", "ai", "model", "llm", "openai", "anthropic", "gemini", "grok"]
    crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "token"]
    if any(k in lower for k in ai_keywords):
        return "AI"
    if any(k in lower for k in crypto_keywords):
        return "crypto"
    return "default"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _normalize_argv(argv: list[str]) -> list[str]:
    """Allow --yes/-y and --config before or after subcommand.

    Moves global flags that appear before the subcommand to after it,
    so argparse subparsers can parse them correctly.
    """
    commands = {"doctor", "add", "list", "remove", "run", "config"}
    # Find subcommand position
    cmd_idx = None
    for i, arg in enumerate(argv):
        if arg in commands:
            cmd_idx = i
            break
    if cmd_idx is None:
        return argv  # no subcommand found, let argparse handle the error

    # Move --yes/-y/--config from before subcommand to after
    before = argv[:cmd_idx]
    after = argv[cmd_idx:]
    relocated = []
    remaining = []
    skip_next = False
    for i, arg in enumerate(before):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--yes", "-y"):
            relocated.append(arg)
        elif arg == "--config":
            relocated.append(arg)
            if i + 1 < len(before):
                relocated.append(before[i + 1])
                skip_next = True
        else:
            remaining.append(arg)
    # Insert relocated flags after the subcommand name
    return remaining + [after[0]] + relocated + after[1:]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SignalRadar v0.5.0 — Polymarket probability monitor"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # doctor
    p_doc = sub.add_parser("doctor", help="Check runtime health")
    p_doc.add_argument("--output", choices=["text", "json"], default="text")
    p_doc.add_argument("--config", default="", help="Path to config JSON")

    # add
    p_add = sub.add_parser("add", help="Add market(s) by Polymarket URL")
    p_add.add_argument("url", help="Polymarket event URL")
    p_add.add_argument("--category", default="", help="Category for the entries")
    p_add.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")
    p_add.add_argument("--config", default="", help="Path to config JSON")

    # list
    p_list = sub.add_parser("list", help="List watchlist entries")
    p_list.add_argument("--category", default="", help="Filter by category")
    p_list.add_argument("--archived", action="store_true", help="Show archived entries")

    # remove
    p_rm = sub.add_parser("remove", help="Remove entry by number")
    p_rm.add_argument("number", type=int, help="Entry number from 'list'")
    p_rm.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")

    # config
    p_cfg = sub.add_parser("config", help="View or change settings")
    p_cfg.add_argument("key", nargs="?", default="", help="Setting name (e.g. check_interval_minutes)")
    p_cfg.add_argument("value", nargs="?", default=None, help="New value")
    p_cfg.add_argument("--output", choices=["text", "json"], default="text")
    p_cfg.add_argument("--config", default="", help="Path to config JSON")

    # run
    p_run = sub.add_parser("run", help="Check all entries for probability changes")
    p_run.add_argument("--dry-run", action="store_true", help="No side effects")
    p_run.add_argument("--output", choices=["text", "json"], default="text")
    p_run.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")
    p_run.add_argument("--config", default="", help="Path to config JSON")

    args = parser.parse_args(_normalize_argv(sys.argv[1:]))

    # Dispatch
    cmd = args.command
    if cmd == "doctor":
        return cmd_doctor(args)
    elif cmd == "add":
        return cmd_add(args)
    elif cmd == "list":
        return cmd_list(args)
    elif cmd == "remove":
        return cmd_remove(args)
    elif cmd == "config":
        return cmd_config(args)
    elif cmd == "run":
        return cmd_run(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
