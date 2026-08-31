#!/usr/bin/env bash
# Build dist/teach-from-source.zip for upload to Claude Cowork.
#
# Cowork expects a zip containing exactly one top-level folder with SKILL.md
# one directory deep. This script produces that, and fails loudly if the two
# builds have drifted apart beyond their two expected frontmatter lines.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/dist/teach-from-source.zip"

CLI="$REPO/claude-code/teach-from-source"
COWORK="$REPO/cowork/teach-from-source"

[ -f "$COWORK/SKILL.md" ] || { echo "error: $COWORK/SKILL.md not found"; exit 1; }

# --- drift check -------------------------------------------------------------
# The two builds must differ ONLY by the two Claude Code frontmatter keys.
# diff exits 1 when files differ, so capture its output rather than piping it
# through a `set -o pipefail` pipeline, where that 1 would mask the result.
DIFF="$(diff -r -x '.DS_Store' "$CLI" "$COWORK" || true)"
UNEXPECTED="$(printf '%s\n' "$DIFF" \
  | grep -vE '^(diff |[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$|< disable-model-invocation: true$|< argument-hint: |---$|$)' \
  || true)"

if [ -z "$UNEXPECTED" ]; then
  echo "ok      builds differ only by the expected CLI-only frontmatter"
else
  echo "warning: claude-code/ and cowork/ have drifted beyond the two frontmatter keys:"
  printf '%s\n' "$UNEXPECTED" | sed 's/^/         /'
fi

if grep -qE '^(disable-model-invocation|argument-hint):' "$COWORK/SKILL.md"; then
  echo "error: cowork SKILL.md still carries Claude Code-only frontmatter; strip it"
  exit 1
fi

# --- build -------------------------------------------------------------------
mkdir -p "$REPO/dist"
rm -f "$OUT"
( cd "$REPO/cowork" && zip -qr "$OUT" teach-from-source -x '*.DS_Store' '__MACOSX/*' )

echo "built   ${OUT#$HOME/}"
echo
unzip -l "$OUT" | sed -n '4,$p' | awk '{ if (NF>=4) print "        " $4 }' | grep -v '^ *$'
echo
echo "Upload this file via Settings -> Skills -> Add -> Upload skill."
