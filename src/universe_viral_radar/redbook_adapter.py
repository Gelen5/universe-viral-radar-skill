from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from .utils import command_exists, ensure_dir, utc_now, write_json


class RedbookNotFound(RuntimeError):
    pass


def _run_json(args: list[str], timeout: int = 300) -> Any:
    if not command_exists("redbook"):
        raise RedbookNotFound(
            "redbook CLI is not installed. Install the optional connector with: "
            "npm install -g @lucasygu/redbook"
        )
    process = subprocess.run(
        ["redbook", *args, "--json"],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "redbook command failed")
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"redbook returned non-JSON output: {process.stdout[:500]}") from exc


def search_notes(keyword: str, out_dir: str | Path, sort: str = "popular", content_type: str = "all") -> Path:
    output = ensure_dir(out_dir)
    args = ["search", keyword, "--sort", sort]
    if content_type != "all":
        args.extend(["--type", content_type])
    data = _run_json(args)
    return write_json(
        output / "redbook-search.json",
        {"kind": "redbook_search", "created_at": utc_now(), "keyword": keyword, "data": data},
    )


def analyze_note(url: str, out_dir: str | Path, comment_pages: int = 3) -> Path:
    output = ensure_dir(out_dir)
    data = _run_json(["analyze-viral", url, "--comment-pages", str(comment_pages)])
    return write_json(
        output / "redbook-note-analysis.json",
        {"kind": "redbook_note_analysis", "created_at": utc_now(), "url": url, "data": data},
    )


def analyze_creator(profile: str, out_dir: str | Path, cooldown_seconds: int = 20) -> Path:
    """Sequential, human-paced calls. Never parallelize platform reads."""
    output = ensure_dir(out_dir)
    profile_data = _run_json(["user", profile])
    time.sleep(max(cooldown_seconds, 0))
    posts_data = _run_json(["user-posts", profile])
    return write_json(
        output / "redbook-creator.json",
        {
            "kind": "redbook_creator",
            "created_at": utc_now(),
            "profile_url_or_id": profile,
            "profile": profile_data,
            "posts": posts_data,
            "research_policy": {"sequential": True, "cooldown_seconds": cooldown_seconds},
        },
    )


def extract_template(urls: list[str], out_dir: str | Path, comment_pages: int = 3) -> Path:
    if not 1 <= len(urls) <= 3:
        raise ValueError("viral-template accepts 1 to 3 URLs")
    output = ensure_dir(out_dir)
    data = _run_json(["viral-template", *urls, "--comment-pages", str(comment_pages)])
    return write_json(
        output / "redbook-viral-template.json",
        {"kind": "redbook_viral_template", "created_at": utc_now(), "urls": urls, "data": data},
    )
