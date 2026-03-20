#!/usr/bin/env python3
"""
三省六部 · 公共工具函数
避免 read_json / now_iso 等基础函数在多个脚本中重复定义
"""
import json, pathlib, datetime, os


def read_json(path, default=None):
    """安全读取 JSON 文件，失败返回 default"""
    try:
        return json.loads(pathlib.Path(path).read_text())
    except Exception:
        return default if default is not None else {}


def now_iso():
    """返回 UTC ISO 8601 时间字符串（末尾 Z）"""
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')


def today_str(fmt='%Y%m%d'):
    """返回今天日期字符串，默认 YYYYMMDD"""
    return datetime.date.today().strftime(fmt)


def safe_name(s: str) -> bool:
    """检查名称是否只含安全字符（字母、数字、下划线、连字符、中文）"""
    import re
    return bool(re.match(r'^[a-zA-Z0-9_\-\u4e00-\u9fff]+$', s))


def validate_url(url: str, allowed_schemes=('https',), allowed_domains=None) -> bool:
    """校验 URL 合法性，防 SSRF"""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if parsed.scheme not in allowed_schemes:
            return False
        if allowed_domains and parsed.hostname not in allowed_domains:
            return False
        if not parsed.hostname:
            return False
        # 禁止内网地址
        import ipaddress
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False
        except ValueError:
            pass  # hostname 不是 IP，放行
        return True
    except Exception:
        return False


def resolve_repo_root(script_path: str | pathlib.Path | None = None) -> pathlib.Path:
    script_file = pathlib.Path(script_path).resolve() if script_path else None
    candidates = []

    def add_candidate(path_like):
        if not path_like:
            return
        p = pathlib.Path(path_like).expanduser().resolve()
        candidates.append(p)
        candidates.extend(p.parents)

    for env_name in ('EDICT_REPO_ROOT', 'OPENCLAW_REPO_ROOT'):
        add_candidate(os.environ.get(env_name))

    add_candidate(pathlib.Path.cwd())
    if script_file:
        add_candidate(script_file.parent)
        add_candidate(script_file.parent.parent)
        for marker_parent in (script_file.parent, script_file.parent.parent):
            marker = marker_parent / '.edict_repo_root'
            if marker.exists():
                try:
                    add_candidate(marker.read_text(encoding='utf-8').strip())
                except Exception:
                    pass

    for candidate in candidates:
        if (
            (candidate / 'agents').is_dir()
            and (candidate / 'scripts').is_dir()
            and (candidate / 'data').exists()
        ):
            return candidate

    if script_file:
        return script_file.parent.parent
    return pathlib.Path.cwd()
