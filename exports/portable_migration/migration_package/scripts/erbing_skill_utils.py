# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace')
"""
ErbingSkillUtils — Hermes-style skill metadata utilities
Based on: NousResearch/hermes-agent agent_skill_utils.py

Key innovations ported:
- Frontmatter parsing (YAML with fallback to simple key:value)
- Platform matching (skills declare platform requirements)
- Disabled skills management (config-based exclusion)
- External skills directories (config.yaml external_dirs)
- Condition extraction (fallback_for_toolsets, requires_toolsets, etc.)
- Skill config extraction (config variable declarations)
- Description extraction (truncated for display)
- File iteration (walk skills dirs with exclusions)
- Namespace parsing (namespace:skill-name format)
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'
SKILLS_DIR = Path('C:/Users/Administrator/.openclaw/workspace/.erbing_skills')

logger = logging.getLogger('erbing')

# Platform mapping
PLATFORM_MAP = {
    "macos": "darwin",
    "linux": "linux",
    "windows": "win32",
}

EXCLUDED_SKILL_DIRS = frozenset((".git", ".github", ".hub"))

# Lazy YAML loader
_yaml_load_fn = None


def yaml_load(content: str):
    """Parse YAML with lazy import and CSafeLoader preference."""
    global _yaml_load_fn
    if _yaml_load_fn is None:
        import yaml
        loader = getattr(yaml, "CSafeLoader", None) or yaml.SafeLoader
        def _load(value: str):
            return yaml.load(value, Loader=loader)
        _yaml_load_fn = _load
    return _yaml_load_fn(content)


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from a markdown string."""
    frontmatter: Dict[str, Any] = {}
    body = content

    if not content.startswith("---"):
        return frontmatter, body

    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return frontmatter, body

    yaml_content = content[3 : end_match.start() + 3]
    body = content[end_match.end() + 3 :]

    try:
        parsed = yaml_load(yaml_content)
        if isinstance(parsed, dict):
            frontmatter = parsed
    except Exception:
        # Fallback: simple key:value parsing
        for line in yaml_content.strip().split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def skill_matches_platform(frontmatter: Dict[str, Any]) -> bool:
    """Return True when skill is compatible with current OS."""
    platforms = frontmatter.get("platforms")
    if not platforms:
        return True
    if not isinstance(platforms, list):
        platforms = [platforms]
    current = sys.platform
    for platform in platforms:
        normalized = str(platform).lower().strip()
        mapped = PLATFORM_MAP.get(normalized, normalized)
        if current.startswith(mapped):
            return True
    return False


def get_disabled_skill_names() -> Set[str]:
    """Read disabled skill names from config."""
    # For Erbing, we can store disabled skills in database
    # For now, return empty set
    return set()


def get_external_skills_dirs() -> List[Path]:
    """Read external skills dirs from config."""
    # For Erbing, we can store external dirs in database
    # For now, return empty list
    return []


def get_all_skills_dirs() -> List[Path]:
    """Return all skill directories: local first, then external."""
    dirs = [SKILLS_DIR]
    dirs.extend(get_external_skills_dirs())
    return dirs


def extract_skill_conditions(frontmatter: Dict[str, Any]) -> Dict[str, List]:
    """Extract conditional activation fields from parsed frontmatter."""
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    hermes = metadata.get("hermes") or {}
    if not isinstance(hermes, dict):
        hermes = {}
    return {
        "fallback_for_toolsets": hermes.get("fallback_for_toolsets", []),
        "requires_toolsets": hermes.get("requires_toolsets", []),
        "fallback_for_tools": hermes.get("fallback_for_tools", []),
        "requires_tools": hermes.get("requires_tools", []),
    }


def extract_skill_config_vars(frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract config variable declarations from parsed frontmatter."""
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        return []
    hermes = metadata.get("hermes")
    if not isinstance(hermes, dict):
        return []
    raw = hermes.get("config")
    if not raw:
        return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []

    result: List[Dict[str, Any]] = []
    seen: set = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        if not key or key in seen:
            continue
        desc = str(item.get("description", "")).strip()
        if not desc:
            continue
        entry: Dict[str, Any] = {
            "key": key,
            "description": desc,
        }
        default = item.get("default")
        if default is not None:
            entry["default"] = default
        prompt_text = item.get("prompt")
        if isinstance(prompt_text, str) and prompt_text.strip():
            entry["prompt"] = prompt_text.strip()
        else:
            entry["prompt"] = desc
        seen.add(key)
        result.append(entry)
    return result


def discover_all_skill_config_vars() -> List[Dict[str, Any]]:
    """Scan all enabled skills and collect their config variable declarations."""
    all_vars: List[Dict[str, Any]] = []
    seen_keys: set = set()

    disabled = get_disabled_skill_names()
    for skills_dir in get_all_skills_dirs():
        if not skills_dir.is_dir():
            continue
        for skill_file in iter_skill_index_files(skills_dir, "SKILL.md"):
            try:
                raw = skill_file.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(raw)
            except Exception:
                continue

            skill_name = frontmatter.get("name") or skill_file.parent.name
            if str(skill_name) in disabled:
                continue
            if not skill_matches_platform(frontmatter):
                continue

            config_vars = extract_skill_config_vars(frontmatter)
            for var in config_vars:
                if var["key"] not in seen_keys:
                    var["skill"] = str(skill_name)
                    all_vars.append(var)
                    seen_keys.add(var["key"])

    return all_vars


SKILL_CONFIG_PREFIX = "skills.config"


def _resolve_dotpath(config: Dict[str, Any], dotted_key: str):
    """Walk a nested dict following a dotted key."""
    parts = dotted_key.split(".")
    current = config
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def resolve_skill_config_values(config_vars: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Resolve current values for skill config vars from config."""
    # For Erbing, we can store config in database
    # For now, return defaults
    resolved: Dict[str, Any] = {}
    for var in config_vars:
        logical_key = var["key"]
        value = var.get("default", "")
        if isinstance(value, str) and ("~" in value or "${" in value):
            value = os.path.expanduser(os.path.expandvars(value))
        resolved[logical_key] = value
    return resolved


def extract_skill_description(frontmatter: Dict[str, Any]) -> str:
    """Extract a truncated description from parsed frontmatter."""
    raw_desc = frontmatter.get("description", "")
    if not raw_desc:
        return ""
    desc = str(raw_desc).strip().strip("'\"")
    if len(desc) > 60:
        return desc[:57] + "..."
    return desc


def iter_skill_index_files(skills_dir: Path, filename: str):
    """Walk skills_dir yielding sorted paths matching filename."""
    matches = []
    for root, dirs, files in os.walk(skills_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_SKILL_DIRS]
        if filename in files:
            matches.append(Path(root) / filename)
    for path in sorted(matches, key=lambda p: str(p.relative_to(skills_dir))):
        yield path


_NAMESPACE_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def parse_qualified_name(name: str) -> Tuple[Optional[str], str]:
    """Split 'namespace:skill-name' into (namespace, bare_name)."""
    if ":" not in name:
        return None, name
    return tuple(name.split(":", 1))


def is_valid_namespace(candidate: Optional[str]) -> bool:
    """Check whether candidate is a valid namespace."""
    if not candidate:
        return False
    return bool(_NAMESPACE_RE.match(candidate))


if __name__ == '__main__':
    print("ErbingSkillUtils loaded.")
    print("Key features:")
    print("  - Frontmatter parsing (YAML with fallback)")
    print("  - Platform matching (skills declare platform requirements)")
    print("  - Disabled skills management (config-based exclusion)")
    print("  - External skills directories (config.yaml external_dirs)")
    print("  - Condition extraction (fallback_for_toolsets, requires_toolsets)")
    print("  - Skill config extraction (config variable declarations)")
    print("  - Description extraction (truncated for display)")
    print("  - File iteration (walk skills dirs with exclusions)")
    print("  - Namespace parsing (namespace:skill-name format)")