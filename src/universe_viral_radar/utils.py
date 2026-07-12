from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: str | Path) -> Path:
    result = Path(path).expanduser().resolve()
    result.mkdir(parents=True, exist_ok=True)
    return result


def read_json(path: str | Path) -> Any:
    with Path(path).expanduser().open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, value: Any) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target.resolve()


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def parse_cn_number(value: Any) -> int:
    """Parse counts such as 123, '1.5万', '2.4亿', or '1,200'."""
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip().replace(",", "").replace("+", "")
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([万亿wWkK]?)", text)
    if not match:
        digits = re.sub(r"[^0-9.-]", "", text)
        try:
            return int(float(digits))
        except (TypeError, ValueError):
            return 0

    number = float(match.group(1))
    unit = match.group(2).lower()
    multiplier = {"": 1, "k": 1_000, "w": 10_000, "万": 10_000, "亿": 100_000_000}[unit]
    return int(number * multiplier)


def repo_root() -> Path:
    # Works in editable installs and directly from the repository.
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "SKILL.md").exists() and (parent / "references").exists():
            return parent
    env_root = os.getenv("VIRAL_RADAR_HOME")
    if env_root:
        return Path(env_root).expanduser().resolve()
    raise RuntimeError("Unable to locate repository root. Set VIRAL_RADAR_HOME.")
