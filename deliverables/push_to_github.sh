#!/usr/bin/env bash
# ==============================================================================
# push_to_github.sh - publish this Docker stack to a GitHub repository.
#
# Usage:
#   ./push_to_github.sh <github-repo-url>
#
# Examples:
#   ./push_to_github.sh https://github.com/<you>/ai-stack.git
#   ./push_to_github.sh git@github.com:<you>/ai-stack.git
#
# What it does:
#   1. git init                (idempotent)
#   2. stages the core DevOps files
#   3. commits: "feat: initial OpenHands + Headroom Docker stack"
#   4. pushes to the given remote on the 'main' branch
#
# Note: create the empty repository on GitHub first, then pass its URL here.
# ==============================================================================
set -euo pipefail

# ---- args -------------------------------------------------------------------
REMOTE_URL="${1:-}"
if [[ -z "$REMOTE_URL" ]]; then
  echo "Usage: ./push_to_github.sh <github-repo-url>" >&2
  echo "Example: ./push_to_github.sh https://github.com/you/ai-stack.git" >&2
  exit 1
fi

BRANCH="main"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log() { printf '\033[0;36m[git]\033[0m %s\n' "$*"; }
ok()  { printf '\033[0;32m[ ok ]\033[0m %s\n' "$*"; }
err() { printf '\033[0;31m[fail]\033[0m %s\n' "$*" >&2; }

command -v git >/dev/null 2>&1 || { err "git is not installed."; exit 1; }

# Core files that make up the IaC bundle (only these are published).
CORE_FILES=(docker-compose.yml .env.example init.sh .gitignore README.md push_to_github.sh)

# ---- 1. init repo -----------------------------------------------------------
if [[ ! -d .git ]]; then
  git init -q
  ok "Initialized empty git repository."
else
  log "Existing git repository detected - reusing it."
fi

# Ensure a committer identity exists (LOCAL to this repo only).
git config user.email >/dev/null 2>&1 || git config user.email "devops@example.com"
git config user.name  >/dev/null 2>&1 || git config user.name  "AI Stack"

# ---- 2. stage core files (explicit + verified) -----------------------------
for f in "${CORE_FILES[@]}"; do
  if [[ -e "$f" ]]; then
    # -f (force) guarantees a stray ignore rule can never drop a core file.
    git add -f -- "$f"
  else
    err "Expected core file '$f' not found in $SCRIPT_DIR - aborting."
    exit 1
  fi
done
# Explicit, per requirement: make sure init.sh is always staged.
git add -f -- init.sh
# Belt-and-suspenders: make sure a real .env is never committed.
git rm --cached -q .env >/dev/null 2>&1 || true
# Verify every core file is actually staged; fail loudly if any is missing.
missing=()
for f in "${CORE_FILES[@]}"; do
  git ls-files --cached --error-unmatch -- "$f" >/dev/null 2>&1 || missing+=("$f")
done
if (( ${#missing[@]} )); then
  err "These core files failed to stage: ${missing[*]}"
  exit 1
fi
ok "Staged & verified core DevOps files: ${CORE_FILES[*]}"

# ---- 3. commit --------------------------------------------------------------
if git diff --cached --quiet; then
  log "No staged changes - skipping commit."
else
  git commit -q -m "feat: initial OpenHands + Headroom Docker stack"
  ok "Created commit: feat: initial OpenHands + Headroom Docker stack"
fi

# ---- 4. push to main --------------------------------------------------------
git branch -M "$BRANCH"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi
ok "Remote 'origin' -> $REMOTE_URL"

log "Pushing to '$BRANCH' ..."
git push -u origin "$BRANCH"
ok "Done. Your stack is live on GitHub."
