"""
Cross-platform JSON file locking helpers.

On Unix this uses fcntl.flock().
On Windows it falls back to msvcrt.locking() on a single-byte lock file.
"""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
from contextlib import contextmanager
from typing import Any, Callable, Iterator

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def _lock_path(path: pathlib.Path) -> pathlib.Path:
    return path.parent / f"{path.name}.lock"


@contextmanager
def _locked_fd(path: pathlib.Path, exclusive: bool) -> Iterator[int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_CREAT | os.O_RDWR)
    try:
        if os.name == "nt":
            mode = msvcrt.LK_LOCK if exclusive else msvcrt.LK_RLCK
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, mode, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield fd
    finally:
        try:
            if os.name == "nt":
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def atomic_json_read(path: pathlib.Path, default: Any = None) -> Any:
    with _locked_fd(_lock_path(path), exclusive=False):
        try:
            return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
        except Exception:
            return default


def atomic_json_update(
    path: pathlib.Path,
    modifier: Callable[[Any], Any],
    default: Any = None,
) -> Any:
    with _locked_fd(_lock_path(path), exclusive=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
        except Exception:
            data = default
        result = modifier(data)
        _atomic_write(path, result)
        return result


def atomic_json_write(path: pathlib.Path, data: Any) -> None:
    with _locked_fd(_lock_path(path), exclusive=True):
        _atomic_write(path, data)


def _atomic_write(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent),
        suffix=".tmp",
        prefix=f"{path.stem}_",
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
