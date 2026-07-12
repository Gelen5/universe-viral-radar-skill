$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/Gelen5/universe-viral-radar-skill.git"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git 未安装，请先安装 Git for Windows。"
}

if (-not (Test-Path ".git")) {
  git init
}

git branch -M main
$remote = git remote 2>$null
if ($remote -contains "origin") {
  git remote set-url origin $RepoUrl
} else {
  git remote add origin $RepoUrl
}

git add .
$changes = git status --porcelain
if ($changes) {
  git commit -m "feat: initialize Universe Viral Radar Skill v0.1.0"
}

git push -u origin main
Write-Host "已推送到 $RepoUrl"
