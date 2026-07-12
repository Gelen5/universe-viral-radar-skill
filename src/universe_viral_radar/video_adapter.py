from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from .utils import ensure_dir, utc_now, write_json


class ClaudeVideoNotFound(RuntimeError):
    pass


def _candidate_watch_dirs() -> list[Path]:
    home = Path.home()
    candidates: list[Path] = []
    explicit = os.getenv("CLAUDE_VIDEO_SKILL_DIR")
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.extend(
        [
            home / ".codex" / "skills" / "watch",
            home / ".agents" / "skills" / "watch",
            home / ".claude" / "skills" / "watch",
            Path.cwd() / ".agents" / "skills" / "watch",
            Path.cwd() / ".codex" / "skills" / "watch",
        ]
    )
    plugin_cache = home / ".claude" / "plugins" / "cache" / "claude-video" / "watch"
    if plugin_cache.exists():
        candidates.extend(sorted(plugin_cache.glob("*/skills/watch"), reverse=True))
    return candidates


def locate_watch_dir() -> Path:
    for candidate in _candidate_watch_dirs():
        if (candidate / "scripts" / "watch.py").is_file():
            return candidate.resolve()
    raise ClaudeVideoNotFound(
        "claude-video /watch skill was not found. Install it with: "
        "npx skills add bradautomates/claude-video -g, or set CLAUDE_VIDEO_SKILL_DIR."
    )


def preflight(watch_dir: Path) -> dict[str, Any]:
    setup_script = watch_dir / "scripts" / "setup.py"
    if not setup_script.exists():
        return {"can_proceed": False, "error": "setup.py not found"}
    process = subprocess.run(
        [sys.executable, str(setup_script), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.stdout.strip():
        try:
            return json.loads(process.stdout)
        except json.JSONDecodeError:
            pass
    return {
        "can_proceed": process.returncode == 0,
        "returncode": process.returncode,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
    }


def _parse_watch_output(raw: str) -> tuple[list[str], list[dict[str, str]]]:
    frame_pattern = re.compile(r"(?P<path>(?:[A-Za-z]:)?[^\n\r\t]*?\.(?:jpe?g|png|webp))", re.I)
    timestamp_pattern = re.compile(r"^\s*\[?(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\]?\s*[-–:]?\s*(?P<text>.+)$")
    frames: list[str] = []
    transcript: list[dict[str, str]] = []
    for line in raw.splitlines():
        frame_match = frame_pattern.search(line)
        if frame_match:
            candidate = frame_match.group("path").strip(" `\"'")
            if "frame" in candidate.lower() and candidate not in frames:
                frames.append(candidate)
        ts_match = timestamp_pattern.match(line)
        if ts_match and len(ts_match.group("text")) > 1:
            transcript.append({"timestamp": ts_match.group("time"), "text": ts_match.group("text").strip()})
    return frames, transcript


def prepare_video(
    source: str,
    out_dir: str | Path,
    detail: str = "balanced",
    start: str | None = None,
    end: str | None = None,
    max_frames: int | None = None,
    resolution: int = 512,
    no_whisper: bool = False,
) -> Path:
    watch_dir = locate_watch_dir()
    output = ensure_dir(out_dir)
    status = preflight(watch_dir)
    if not status.get("can_proceed", False):
        raise RuntimeError(
            "claude-video preflight did not pass. Run: "
            f"{sys.executable} {watch_dir / 'scripts' / 'setup.py'}\n"
            f"Status: {json.dumps(status, ensure_ascii=False)}"
        )

    command = [
        sys.executable,
        str(watch_dir / "scripts" / "watch.py"),
        source,
        "--detail",
        detail,
        "--resolution",
        str(resolution),
        "--out-dir",
        str(output),
    ]
    if start:
        command.extend(["--start", start])
    if end:
        command.extend(["--end", end])
    if max_frames is not None:
        command.extend(["--max-frames", str(max_frames)])
    if no_whisper:
        command.append("--no-whisper")

    process = subprocess.run(command, capture_output=True, text=True, check=False)
    raw = (process.stdout or "") + (("\n" + process.stderr) if process.stderr else "")
    raw_path = output / "claude-video-output.txt"
    raw_path.write_text(raw, encoding="utf-8")
    if process.returncode != 0:
        raise RuntimeError(f"claude-video failed with exit code {process.returncode}. See {raw_path}")

    frames, transcript = _parse_watch_output(raw)
    manifest = {
        "schema_version": "1.0",
        "kind": "video_evidence",
        "created_at": utc_now(),
        "source": source,
        "adapter": "bradautomates/claude-video",
        "watch_dir": str(watch_dir),
        "detail": detail,
        "focus": {"start": start, "end": end},
        "frames": frames,
        "transcript_segments": transcript,
        "raw_output": str(raw_path),
        "command": command,
        "notes": [
            "Frame paths and transcript are parsed on a best-effort basis.",
            "The AI agent should read claude-video-output.txt and inspect all listed frames before analysis.",
        ],
    }
    return write_json(output / "video-evidence.json", manifest)
