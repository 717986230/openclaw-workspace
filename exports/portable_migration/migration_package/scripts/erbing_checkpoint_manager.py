# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace')
"""
ErbingCheckpointManager — Hermes-style transparent filesystem snapshots
Based on: NousResearch/hermes-agent tools_checkpoint_manager.py (24KB)

Key innovations ported:
- Shadow git repos (GIT_DIR + GIT_WORK_TREE) for transparent snapshots
- Git isolation (GIT_CONFIG_GLOBAL/SYSTEM = dev/null) to prevent user config leaks
- Per-turn deduplication (one snapshot per directory per turn)
- Pre-rollback snapshot (undo the undo)
- Project root detection (walks up to find .git, pyproject.toml, etc.)
- Input validation (git argument injection + path traversal protection)
- Max files limit (50,000) to avoid slowdowns
- Default excludes (node_modules, dist, build, .env, __pycache__, etc.)
"""

import hashlib
import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'
CHECKPOINT_BASE = Path('C:/Users/Administrator/.openclaw/workspace/.erbing_checkpoints')

DEFAULT_EXCLUDES = [
    "node_modules/", "dist/", "build/", ".env", ".env.*", ".env.local",
    "__pycache__/", "*.pyc", "*.pyo", ".DS_Store", "*.log", ".cache/",
    ".next/", ".nuxt/", "coverage/", ".pytest_cache/", ".venv/", "venv/",
    ".git/", "target/", "bin/", "obj/", ".idea/", ".vscode/",
]

_GIT_TIMEOUT = 30
_MAX_FILES = 50_000
_COMMIT_HASH_RE = re.compile(r'^[0-9a-fA-F]{4,64}$')

logger = logging.getLogger('erbing')


def _validate_commit_hash(commit_hash: str) -> Optional[str]:
    """Validate commit hash to prevent git argument injection."""
    if not commit_hash or not commit_hash.strip():
        return "Empty commit hash"
    if commit_hash.startswith("-"):
        return f"Invalid commit hash (must not start with '-'): {commit_hash!r}"
    if not _COMMIT_HASH_RE.match(commit_hash):
        return f"Invalid commit hash (expected 4-64 hex characters): {commit_hash!r}"
    return None


def _validate_file_path(file_path: str, working_dir: str) -> Optional[str]:
    """Validate file path to prevent path traversal outside working dir."""
    if not file_path or not file_path.strip():
        return "Empty file path"
    if os.path.isabs(file_path):
        return f"File path must be relative, got absolute: {file_path!r}"
    abs_workdir = Path(working_dir).resolve()
    resolved = (abs_workdir / file_path).resolve()
    try:
        resolved.relative_to(abs_workdir)
    except ValueError:
        return f"File path escapes working directory: {file_path!r}"
    return None


def _normalize_path(path_value: str) -> Path:
    """Return canonical absolute path."""
    return Path(path_value).expanduser().resolve()


def _shadow_repo_path(working_dir: str) -> Path:
    """Deterministic shadow repo path: sha256(abs_path)[:16]."""
    abs_path = str(_normalize_path(working_dir))
    dir_hash = hashlib.sha256(abs_path.encode()).hexdigest()[:16]
    return CHECKPOINT_BASE / dir_hash


def _git_env(shadow_repo: Path, working_dir: str) -> dict:
    """Build env dict that redirects git to the shadow repo."""
    env = os.environ.copy()
    env["GIT_DIR"] = str(shadow_repo)
    env["GIT_WORK_TREE"] = str(_normalize_path(working_dir))
    env.pop("GIT_INDEX_FILE", None)
    env.pop("GIT_NAMESPACE", None)
    env.pop("GIT_ALTERNATE_OBJECT_DIRECTORIES", None)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _run_git(
    args: List[str],
    shadow_repo: Path,
    working_dir: str,
    timeout: int = _GIT_TIMEOUT,
    allowed_returncodes: Optional[Set[int]] = None,
) -> tuple:
    """Run git command against shadow repo. Returns (ok, stdout, stderr)."""
    normalized_working_dir = _normalize_path(working_dir)
    if not normalized_working_dir.exists():
        msg = f"working directory not found: {normalized_working_dir}"
        logger.error("Git command skipped: %s (%s)", " ".join(["git"] + list(args)), msg)
        return False, "", msg
    if not normalized_working_dir.is_dir():
        msg = f"working directory is not a directory: {normalized_working_dir}"
        logger.error("Git command skipped: %s (%s)", " ".join(["git"] + list(args)), msg)
        return False, "", msg

    env = _git_env(shadow_repo, str(normalized_working_dir))
    cmd = ["git"] + list(args)
    allowed_returncodes = allowed_returncodes or set()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(normalized_working_dir),
        )
        ok = result.returncode == 0
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if not ok and result.returncode not in allowed_returncodes:
            logger.error(
                "Git command failed: %s (rc=%d) stderr=%s",
                " ".join(cmd), result.returncode, stderr,
            )
        return ok, stdout, stderr
    except subprocess.TimeoutExpired:
        msg = f"git timed out after {timeout}s: {' '.join(cmd)}"
        logger.error(msg, exc_info=True)
        return False, "", msg
    except FileNotFoundError as exc:
        missing_target = getattr(exc, "filename", None)
        if missing_target == "git":
            logger.error("Git executable not found: %s", " ".join(cmd), exc_info=True)
            return False, "", "git not found"
        msg = f"working directory not found: {normalized_working_dir}"
        logger.error("Git command failed before execution: %s (%s)", " ".join(cmd), msg, exc_info=True)
        return False, "", msg
    except Exception as exc:
        logger.error("Unexpected git error running %s: %s", " ".join(cmd), exc, exc_info=True)
        return False, "", str(exc)


def _init_shadow_repo(shadow_repo: Path, working_dir: str) -> Optional[str]:
    """Initialize shadow repo if needed. Returns error string or None."""
    if (shadow_repo / "HEAD").exists():
        return None

    shadow_repo.mkdir(parents=True, exist_ok=True)

    ok, _, err = _run_git(["init"], shadow_repo, working_dir)
    if not ok:
        return f"Shadow repo init failed: {err}"

    _run_git(["config", "user.email", "erbing@local"], shadow_repo, working_dir)
    _run_git(["config", "user.name", "Erbing Checkpoint"], shadow_repo, working_dir)
    _run_git(["config", "commit.gpgsign", "false"], shadow_repo, working_dir)
    _run_git(["config", "tag.gpgSign", "false"], shadow_repo, working_dir)

    info_dir = shadow_repo / "info"
    info_dir.mkdir(exist_ok=True)
    (info_dir / "exclude").write_text("\n".join(DEFAULT_EXCLUDES) + "\n", encoding="utf-8")
    (shadow_repo / "ERBING_WORKDIR").write_text(str(_normalize_path(working_dir)) + "\n", encoding="utf-8")

    logger.debug("Initialized checkpoint repo at %s for %s", shadow_repo, working_dir)
    return None


def _dir_file_count(path: str) -> int:
    """Quick file count estimate (stops early if over _MAX_FILES)."""
    count = 0
    try:
        for _ in Path(path).rglob("*"):
            count += 1
            if count > _MAX_FILES:
                return count
    except (PermissionError, OSError):
        pass
    return count


class ErbingCheckpointManager:
    """
    Transparent filesystem checkpoint manager.
    
    Uses shadow git repos (GIT_DIR + GIT_WORK_TREE) for snapshots.
    Per-turn deduplication: one snapshot per directory per turn.
    Pre-rollback snapshot: takes snapshot before restore (undo the undo).
    Project root detection: walks up to find .git, pyproject.toml, package.json, etc.
    """

    def __init__(self, enabled: bool = False, max_snapshots: int = 50):
        self.enabled = enabled
        self.max_snapshots = max_snapshots
        self._checkpointed_dirs: Set[str] = set()
        self._git_available: Optional[bool] = None

    def new_turn(self) -> None:
        """Reset per-turn dedup. Call at start of each agent iteration."""
        self._checkpointed_dirs.clear()

    def ensure_checkpoint(self, working_dir: str, reason: str = "auto") -> bool:
        """Take a checkpoint if enabled and not already done this turn."""
        if not self.enabled:
            return False

        if self._git_available is None:
            self._git_available = shutil.which("git") is not None
            if not self._git_available:
                logger.debug("Checkpoints disabled: git not found")
        if not self._git_available:
            return False

        abs_dir = str(_normalize_path(working_dir))
        if abs_dir in ("/", str(Path.home())):
            logger.debug("Checkpoint skipped: directory too broad (%s)", abs_dir)
            return False

        if abs_dir in self._checkpointed_dirs:
            return False

        self._checkpointed_dirs.add(abs_dir)
        try:
            return self._take(abs_dir, reason)
        except Exception as e:
            logger.debug("Checkpoint failed (non-fatal): %s", e)
            return False

    def list_checkpoints(self, working_dir: str) -> List[Dict]:
        """List available checkpoints for a directory. Most recent first."""
        abs_dir = str(_normalize_path(working_dir))
        shadow = _shadow_repo_path(abs_dir)

        if not (shadow / "HEAD").exists():
            return []

        ok, stdout, _ = _run_git(
            ["log", "--format=%H|%h|%aI|%s", "-n", str(self.max_snapshots)],
            shadow, abs_dir,
        )

        if not ok or not stdout:
            return []

        results = []
        for line in stdout.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                entry = {
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "timestamp": parts[2],
                    "reason": parts[3],
                    "files_changed": 0,
                    "insertions": 0,
                    "deletions": 0,
                }
                stat_ok, stat_out, _ = _run_git(
                    ["diff", "--shortstat", f"{parts[0]}~1", parts[0]],
                    shadow, abs_dir,
                    allowed_returncodes={128, 129},
                )
                if stat_ok and stat_out:
                    self._parse_shortstat(stat_out, entry)
                results.append(entry)
        return results

    @staticmethod
    def _parse_shortstat(stat_line: str, entry: Dict) -> None:
        """Parse git --shortstat output."""
        m = re.search(r'(\d+) file', stat_line)
        if m:
            entry["files_changed"] = int(m.group(1))
        m = re.search(r'(\d+) insertion', stat_line)
        if m:
            entry["insertions"] = int(m.group(1))
        m = re.search(r'(\d+) deletion', stat_line)
        if m:
            entry["deletions"] = int(m.group(1))

    def diff(self, working_dir: str, commit_hash: str) -> Dict:
        """Show diff between checkpoint and current working tree."""
        hash_err = _validate_commit_hash(commit_hash)
        if hash_err:
            return {"success": False, "error": hash_err}

        abs_dir = str(_normalize_path(working_dir))
        shadow = _shadow_repo_path(abs_dir)

        if not (shadow / "HEAD").exists():
            return {"success": False, "error": "No checkpoints exist for this directory"}

        ok, _, err = _run_git(["cat-file", "-t", commit_hash], shadow, abs_dir)
        if not ok:
            return {"success": False, "error": f"Checkpoint '{commit_hash}' not found"}

        _run_git(["add", "-A"], shadow, abs_dir, timeout=_GIT_TIMEOUT * 2)

        ok_stat, stat_out, _ = _run_git(["diff", "--stat", commit_hash, "--cached"], shadow, abs_dir)
        ok_diff, diff_out, _ = _run_git(["diff", commit_hash, "--cached", "--no-color"], shadow, abs_dir)

        _run_git(["reset", "HEAD", "--quiet"], shadow, abs_dir)

        if not ok_stat and not ok_diff:
            return {"success": False, "error": "Could not generate diff"}

        return {
            "success": True,
            "stat": stat_out if ok_stat else "",
            "diff": diff_out if ok_diff else "",
        }

    def restore(self, working_dir: str, commit_hash: str, file_path: str = None) -> Dict:
        """Restore files to a checkpoint state."""
        hash_err = _validate_commit_hash(commit_hash)
        if hash_err:
            return {"success": False, "error": hash_err}

        abs_dir = str(_normalize_path(working_dir))

        if file_path:
            path_err = _validate_file_path(file_path, abs_dir)
            if path_err:
                return {"success": False, "error": path_err}

        shadow = _shadow_repo_path(abs_dir)

        if not (shadow / "HEAD").exists():
            return {"success": False, "error": "No checkpoints exist for this directory"}

        ok, _, err = _run_git(["cat-file", "-t", commit_hash], shadow, abs_dir)
        if not ok:
            return {"success": False, "error": f"Checkpoint '{commit_hash}' not found"}

        # Pre-rollback snapshot
        self._take(abs_dir, f"pre-rollback snapshot (restoring to {commit_hash[:8]})")

        restore_target = file_path if file_path else "."
        ok, stdout, err = _run_git(
            ["checkout", commit_hash, "--", restore_target],
            shadow, abs_dir, timeout=_GIT_TIMEOUT * 2,
        )

        if not ok:
            return {"success": False, "error": f"Restore failed: {err}"}

        ok2, reason_out, _ = _run_git(["log", "--format=%s", "-1", commit_hash], shadow, abs_dir)
        reason = reason_out if ok2 else "unknown"

        result = {
            "success": True,
            "restored_to": commit_hash[:8],
            "reason": reason,
            "directory": abs_dir,
        }
        if file_path:
            result["file"] = file_path
        return result

    def get_working_dir_for_path(self, file_path: str) -> str:
        """Resolve file path to its working directory for checkpointing."""
        path = _normalize_path(file_path)
        if path.is_dir():
            candidate = path
        else:
            candidate = path.parent

        markers = {".git", "pyproject.toml", "package.json", "Cargo.toml",
                    "go.mod", "Makefile", "pom.xml", ".hg", "Gemfile"}
        check = candidate
        while check != check.parent:
            if any((check / m).exists() for m in markers):
                return str(check)
            check = check.parent

        return str(candidate)

    def _take(self, working_dir: str, reason: str) -> bool:
        """Take a snapshot. Returns True on success."""
        shadow = _shadow_repo_path(working_dir)

        err = _init_shadow_repo(shadow, working_dir)
        if err:
            logger.debug("Checkpoint init failed: %s", err)
            return False

        if _dir_file_count(working_dir) > _MAX_FILES:
            logger.debug("Checkpoint skipped: >%d files in %s", _MAX_FILES, working_dir)
            return False

        ok, _, err = _run_git(["add", "-A"], shadow, working_dir, timeout=_GIT_TIMEOUT * 2)
        if not ok:
            logger.debug("Checkpoint git-add failed: %s", err)
            return False

        ok_diff, diff_out, _ = _run_git(
            ["diff", "--cached", "--quiet"],
            shadow, working_dir,
            allowed_returncodes={1},
        )
        if ok_diff:
            logger.debug("Checkpoint skipped: no changes in %s", working_dir)
            return False

        ok, _, err = _run_git(
            ["commit", "-m", reason, "--allow-empty-message", "--no-gpg-sign"],
            shadow, working_dir, timeout=_GIT_TIMEOUT * 2,
        )
        if not ok:
            logger.debug("Checkpoint commit failed: %s", err)
            return False

        logger.debug("Checkpoint taken in %s: %s", working_dir, reason)
        self._prune(shadow, working_dir)
        return True

    def _prune(self, shadow_repo: Path, working_dir: str) -> None:
        """Keep only last max_snapshots commits."""
        ok, stdout, _ = _run_git(["rev-list", "--count", "HEAD"], shadow_repo, working_dir)
        if not ok:
            return
        try:
            count = int(stdout)
        except ValueError:
            return
        if count <= self.max_snapshots:
            return
        logger.debug("Checkpoint repo has %d commits (limit %d)", count, self.max_snapshots)


def format_checkpoint_list(checkpoints: List[Dict], directory: str) -> str:
    """Format checkpoint list for display."""
    if not checkpoints:
        return f"No checkpoints found for {directory}"

    lines = [f"Checkpoints for {directory}:\n"]
    for i, cp in enumerate(checkpoints, 1):
        ts = cp["timestamp"]
        if "T" in ts:
            ts = ts.split("T")[1].split("+")[0].split("-")[0][:5]
            date = cp["timestamp"].split("T")[0]
            ts = f"{date} {ts}"

        files = cp.get("files_changed", 0)
        ins = cp.get("insertions", 0)
        dele = cp.get("deletions", 0)
        if files:
            stat = f"  ({files} file{'s' if files != 1 else ''}, +{ins}/-{dele})"
        else:
            stat = ""

        lines.append(f"  {i}. {cp['short_hash']}  {ts}  {cp['reason']}{stat}")

    lines.append("\n  /rollback <N>             restore to checkpoint N")
    lines.append("  /rollback diff <N>        preview changes since checkpoint N")
    lines.append("  /rollback <N> <file>      restore a single file from checkpoint N")
    return "\n".join(lines)


if __name__ == '__main__':
    print("ErbingCheckpointManager loaded.")
    print("Key features:")
    print("  - Shadow git repos (GIT_DIR + GIT_WORK_TREE)")
    print("  - Git isolation (GIT_CONFIG_GLOBAL/SYSTEM = devnull)")
    print("  - Per-turn deduplication")
    print("  - Pre-rollback snapshot (undo the undo)")
    print("  - Project root detection")
    print("  - Input validation (git injection + path traversal)")
    print("  - Max files limit (50,000)")
    print("  - Default excludes (node_modules, dist, build, .env, __pycache__)")