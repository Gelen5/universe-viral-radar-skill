#!/usr/bin/env python3
"""Repository-local entry point without installation."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from universe_viral_radar.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
