#!/usr/bin/env bash
# Bootstrap ai-config on a machine: install the maintenance skills for Claude Code and Cursor,
# and record the clone path + local exclusions in ~/.ai-config/ (machine-local, never synced).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="${AI_CONFIG_HOME:-$HOME}"
STATE="$HOME_DIR/.ai-config"
MAINT=(merge-ai-config pull-ai-config update-harness set-local)

for s in "${MAINT[@]}"; do
  [[ -f "$REPO_ROOT/skills/$s/SKILL.md" ]] || { echo "bootstrap: error: missing $REPO_ROOT/skills/$s/SKILL.md" >&2; exit 1; }
done

# Older setups symlinked ~/.claude/{skills,agents,rules} into a repo. Broken links would make every write fail.
for d in skills agents rules; do
  link="$HOME_DIR/.claude/$d"
  if [[ -L "$link" && ! -e "$link" ]]; then
    echo "bootstrap: removing broken symlink $link -> $(readlink "$link")"
    rm "$link"
  elif [[ -L "$link" ]]; then
    echo "bootstrap: warning: $link is a symlink to $(readlink "$link"); merge will write through it" >&2
  fi
done

install_to() {
  local dest="$1"
  mkdir -p "$dest"
  for s in "${MAINT[@]}"; do
    mkdir -p "$dest/$s"
    cp -R "$REPO_ROOT/skills/$s/." "$dest/$s/"
  done
  echo "bootstrap: installed maintenance skills → $dest"
}
install_to "$HOME_DIR/.claude/skills"
install_to "$HOME_DIR/.agents/skills"   # Cursor user skills

mkdir -p "$STATE"
printf '%s\n' "$REPO_ROOT" > "$STATE/repo-path"

if [[ ! -f "$STATE/local.md" ]]; then
  cat > "$STATE/local.md" <<'LOCAL'
# Local exclusions (machine-only, never committed)

Names listed here are skipped by /merge-ai-config, /update-harness and lib/ai_sync.py on this machine.
They stay on the machine where they are; they are never written to the repo or adopted from it.

## Skills

<!-- skill folder names, one per line -->

## Agents

<!-- agent filename stems, one per line -->

## Rules

<!-- rule stems, one per line -->
LOCAL
fi

echo "bootstrap: repo path → $STATE/repo-path"
echo "Next: in Claude Code or Cursor run /merge-ai-config"
