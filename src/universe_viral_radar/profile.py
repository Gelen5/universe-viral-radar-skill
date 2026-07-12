from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .utils import read_json, repo_root, write_json

REQUIRED_PROFILE_KEYS = {
    "identity",
    "target_audience",
    "content_pillars",
    "voice",
    "products",
    "constraints",
    "goals",
}


def init_profile(destination: str | Path, force: bool = False) -> Path:
    destination = Path(destination).expanduser().resolve()
    source = repo_root() / "profiles" / "creator-profile.template.json"
    if destination.exists() and not force:
        raise FileExistsError(f"Profile already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return destination


def validate_profile(path: str | Path) -> tuple[bool, list[str], dict[str, Any]]:
    data = read_json(path)
    missing = sorted(REQUIRED_PROFILE_KEYS - set(data))
    errors: list[str] = []
    if missing:
        errors.append("Missing keys: " + ", ".join(missing))
    if not isinstance(data.get("content_pillars", []), list):
        errors.append("content_pillars must be a list")
    if not isinstance(data.get("products", []), list):
        errors.append("products must be a list")
    return not errors, errors, data


def save_profile(path: str | Path, data: dict[str, Any]) -> Path:
    return write_json(path, data)
