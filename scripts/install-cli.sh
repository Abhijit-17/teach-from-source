#!/usr/bin/env bash
# Install the Claude Code CLI build of teach-from-source into ~/.claude/skills/.
#
#   ./scripts/install-cli.sh            copy (stable)
#   ./scripts/install-cli.sh --link     symlink (tracks this repo)

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/claude-code/teach-from-source"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/teach-from-source"

[ -f "$SRC/SKILL.md" ] || { echo "error: $SRC/SKILL.md not found"; exit 1; }

mkdir -p "$(dirname "$DEST")"

if [ -L "$DEST" ]; then
  # A symlink from a previous --link install: drop the link, never the target.
  rm -f "$DEST"
  echo "note: removed previous symlink at $DEST"
elif [ -d "$DEST" ]; then
  # Never delete a real directory; it may hold local edits. Move it aside.
  BAK="$DEST.bak-$(date +%Y%m%d-%H%M%S)"
  mv "$DEST" "$BAK"
  echo "note: existing install backed up to $BAK"
elif [ -e "$DEST" ]; then
  echo "error: $DEST exists and is not a directory or symlink; move it aside first"
  exit 1
fi

if [ "${1:-}" = "--link" ]; then
  ln -s "$SRC" "$DEST"
  echo "linked  $DEST -> $SRC"
else
  cp -R "$SRC" "$DEST"
  find "$DEST" -name '.DS_Store' -delete
  echo "copied  $SRC -> $DEST"
fi

grep -q '^disable-model-invocation: true' "$DEST/SKILL.md" \
  || echo "warning: installed SKILL.md lacks disable-model-invocation, so Claude may auto-invoke it"

echo
echo "Restart 'claude', then invoke with:  /teach-from-source <source>"
echo "followed by what you want out of it. See docs/example-prompts.md."
