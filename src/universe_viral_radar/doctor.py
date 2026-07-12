from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .video_adapter import ClaudeVideoNotFound, locate_watch_dir, preflight


def run_doctor() -> dict[str, Any]:
    report: dict[str, Any] = {
        "python": shutil.which("python3") or shutil.which("python"),
        "ffmpeg": shutil.which("ffmpeg"),
        "yt_dlp": shutil.which("yt-dlp"),
        "redbook": shutil.which("redbook"),
        "claude_video": None,
        "claude_video_preflight": None,
    }
    try:
        watch_dir = locate_watch_dir()
        report["claude_video"] = str(watch_dir)
        report["claude_video_preflight"] = preflight(watch_dir)
    except ClaudeVideoNotFound as exc:
        report["claude_video_error"] = str(exc)
    return report


def format_doctor(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
