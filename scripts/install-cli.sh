#!/usr/bin/env bash
# Install the Claude Code CLI build of teach-from-source into ~/.claude/skills/.
#
#   ./scripts/install-cli.sh            copy (stable)
#   ./scripts/install-cli.sh --link     symlink (tracks this repo)

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/claude-code/teach-from-source"
SKILLS="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
DEST="$SKILLS/teach-from-source"
# Backups live beside the skills folder, never in it: Claude Code loads every
# folder in it as a skill, and the skill's own setup search could find one.
BACKUPS="$(dirname "$SKILLS")/skill-backups"

[ -f "$SRC/SKILL.md" ] || { echo "error: $SRC/SKILL.md not found"; exit 1; }

mkdir -p "$(dirname "$DEST")"

# Earlier versions of this script left their backups inside the skills
# folder. Move any found there out, for the same reason.
for OLD in "$SKILLS"/teach-from-source.bak-*; do
  [ -e "$OLD" ] || [ -L "$OLD" ] || continue   # the pattern matched nothing
  mkdir -p "$BACKUPS"
  TO="$BACKUPS/$(basename "$OLD")"
  n=2
  while [ -e "$TO" ] || [ -L "$TO" ]; do TO="$BACKUPS/$(basename "$OLD").$n"; n=$((n + 1)); done
  mv "$OLD" "$TO"
  echo "note: moved an old backup out of the skills folder to $TO"
done

if [ -L "$DEST" ]; then
  # A symlink from a previous --link install: drop the link, never the target.
  rm -f "$DEST"
  echo "note: removed previous symlink at $DEST"
elif [ -d "$DEST" ]; then
  # Never delete a real directory; it may hold local edits. Move it aside.
  mkdir -p "$BACKUPS"
  BAK="$BACKUPS/teach-from-source.bak-$(date +%Y%m%d-%H%M%S)"
  # date resolves to the second, so two installs in the same second would
  # otherwise collide and mv would nest the second one inside the first backup.
  n=2
  while [ -e "$BAK" ]; do BAK="$BACKUPS/teach-from-source.bak-$(date +%Y%m%d-%H%M%S).$n"; n=$((n + 1)); done
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
