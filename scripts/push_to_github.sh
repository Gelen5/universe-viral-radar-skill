#!/usr/bin/env bash
set -euo pipefail
REPO_URL="https://github.com/Gelen5/universe-viral-radar-skill.git"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v git >/dev/null 2>&1 || { echo "Git is required." >&2; exit 1; }
[ -d .git ] || git init
git branch -M main
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi
git add .
if ! git diff --cached --quiet; then
  git commit -m "feat: initialize Universe Viral Radar Skill v0.1.0"
fi
git push -u origin main
