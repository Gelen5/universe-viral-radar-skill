from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .utils import repo_root

MODE_REFERENCES = {
    "video": ["evidence-rules.md", "video-breakdown.md", "viral-structure.md"],
    "creator": ["evidence-rules.md", "creator-analysis.md", "monetization-path.md"],
    "script": ["evidence-rules.md", "personalized-script.md", "prepublish-check.md"],
    "prepublish": [
        "evidence-rules.md",
        "prepublish-check.md",
        "platforms/common-short-video-rules.md",
        "platforms/xiaohongshu-rules.md",
        "platforms/douyin-rules.md",
        "platforms/wechat-channels-rules.md",
        "prepublish/common-checklist.md",
        "prepublish/xiaohongshu-checklist.md",
        "prepublish/douyin-checklist.md",
        "prepublish/wechat-channels-checklist.md",
    ],
    "full": [
        "evidence-rules.md",
        "video-breakdown.md",
        "creator-analysis.md",
        "monetization-path.md",
        "viral-structure.md",
        "personalized-script.md",
        "prepublish-check.md",
        "platforms/common-short-video-rules.md",
        "platforms/xiaohongshu-rules.md",
        "platforms/douyin-rules.md",
        "platforms/wechat-channels-rules.md",
        "prepublish/common-checklist.md",
        "prepublish/xiaohongshu-checklist.md",
        "prepublish/douyin-checklist.md",
        "prepublish/wechat-channels-checklist.md",
    ],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_context(mode: str, evidence_files: Iterable[str], profile_file: str | None, output_file: str) -> Path:
    if mode not in MODE_REFERENCES:
        raise ValueError(f"Unsupported mode: {mode}")
    root = repo_root()
    chunks = [f"# Universe Viral Radar Context\n\nMode: `{mode}`\n"]
    for name in MODE_REFERENCES[mode]:
        chunks.append(f"\n---\n\n# Reference: {name}\n\n{_read(root / 'references' / Path(name))}")
    if profile_file:
        profile = Path(profile_file).expanduser().resolve()
        chunks.append(f"\n---\n\n# Creator Profile: {profile.name}\n\n```json\n{_read(profile)}\n```")
    for file_name in evidence_files:
        path = Path(file_name).expanduser().resolve()
        chunks.append(f"\n---\n\n# Evidence: {path.name}\n\n```\n{_read(path)}\n```")
    target = Path(output_file).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(chunks) + "\n", encoding="utf-8")
    return target
