#!/usr/bin/env bash
# Bootstrap ai-config on a machine: install (render) the maintenance skills for Claude Code and Cursor and verify them,
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

ONLY=()
for s in "${MAINT[@]}"; do ONLY+=(--only "skills:$s"); done
SYNC=(python3 "$REPO_ROOT/lib/ai_sync.py")

"${SYNC[@]}" install --repo "$REPO_ROOT" --home "$HOME_DIR" --tool both "${ONLY[@]}" >/dev/null
echo "bootstrap: installed maintenance skills → $HOME_DIR/.claude/skills, $HOME_DIR/.agents/skills"

for tool in claude cursor; do
  "${SYNC[@]}" verify --repo "$REPO_ROOT" --home "$HOME_DIR" --tool "$tool" "${ONLY[@]}" \
    || { echo "bootstrap: error: verify --tool $tool failed" >&2; exit 1; }
done

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
