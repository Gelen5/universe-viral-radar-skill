from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .context_builder import build_context
from .doctor import format_doctor, run_doctor
from .profile import init_profile, validate_profile
from .redbook_adapter import analyze_creator, analyze_note, extract_template, search_notes
from .scoring import score_benchmark
from .utils import read_json, write_json
from .video_adapter import prepare_video


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="viral-radar", description="Universe Viral Radar helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check optional dependencies and adapters")

    init = sub.add_parser("init-profile", help="Create a creator profile template")
    init.add_argument("path", nargs="?", default="creator-profile.json")
    init.add_argument("--force", action="store_true")

    validate = sub.add_parser("validate-profile", help="Validate a creator profile")
    validate.add_argument("path")

    video = sub.add_parser("video", help="Prepare video evidence through claude-video")
    video.add_argument("source")
    video.add_argument("--out", default="workspaces/video")
    video.add_argument("--detail", choices=["transcript", "efficient", "balanced", "token-burner"], default="balanced")
    video.add_argument("--start")
    video.add_argument("--end")
    video.add_argument("--max-frames", type=int)
    video.add_argument("--resolution", type=int, default=512)
    video.add_argument("--no-whisper", action="store_true")

    redbook = sub.add_parser("redbook", help="Use optional redbook connector")
    red_sub = redbook.add_subparsers(dest="redbook_command", required=True)
    search = red_sub.add_parser("search")
    search.add_argument("keyword")
    search.add_argument("--out", default="workspaces/redbook-search")
    search.add_argument("--sort", choices=["general", "popular", "latest"], default="popular")
    search.add_argument("--type", choices=["all", "video", "image"], default="all")
    note = red_sub.add_parser("note")
    note.add_argument("url")
    note.add_argument("--out", default="workspaces/redbook-note")
    note.add_argument("--comment-pages", type=int, default=3)
    creator = red_sub.add_parser("creator")
    creator.add_argument("profile")
    creator.add_argument("--out", default="workspaces/redbook-creator")
    creator.add_argument("--cooldown", type=int, default=20)
    template = red_sub.add_parser("template")
    template.add_argument("urls", nargs="+")
    template.add_argument("--out", default="workspaces/redbook-template")
    template.add_argument("--comment-pages", type=int, default=3)

    context = sub.add_parser("build-context", help="Combine references, profile and evidence for an AI agent")
    context.add_argument("--mode", choices=["video", "creator", "script", "prepublish", "full"], default="full")
    context.add_argument("--profile")
    context.add_argument("--evidence", action="append", default=[])
    context.add_argument("--out", default="workspaces/context.md")

    score = sub.add_parser("score-benchmark", help="Calculate benchmark-account fit score")
    score.add_argument("input", help="JSON file with 0-10 dimension values")
    score.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            print(format_doctor(run_doctor()))
            return 0
        if args.command == "init-profile":
            print(init_profile(args.path, args.force))
            return 0
        if args.command == "validate-profile":
            ok, errors, _ = validate_profile(args.path)
            print(json.dumps({"valid": ok, "errors": errors}, ensure_ascii=False, indent=2))
            return 0 if ok else 2
        if args.command == "video":
            print(prepare_video(args.source, args.out, args.detail, args.start, args.end, args.max_frames, args.resolution, args.no_whisper))
            return 0
        if args.command == "redbook":
            if args.redbook_command == "search":
                print(search_notes(args.keyword, args.out, args.sort, args.type))
            elif args.redbook_command == "note":
                print(analyze_note(args.url, args.out, args.comment_pages))
            elif args.redbook_command == "creator":
                print(analyze_creator(args.profile, args.out, args.cooldown))
            elif args.redbook_command == "template":
                print(extract_template(args.urls, args.out, args.comment_pages))
            return 0
        if args.command == "build-context":
            print(build_context(args.mode, args.evidence, args.profile, args.out))
            return 0
        if args.command == "score-benchmark":
            result = score_benchmark(read_json(args.input))
            if args.out:
                print(write_json(args.out, result))
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    except (RuntimeError, ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
