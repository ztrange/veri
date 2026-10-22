#!/bin/sh
# extract-result.sh — pull the final assistant text out of a claude stream-json stream: a shim over veri/extract_result.py.
#
# Writes the newest result record whose text carries a `VERDICT:`, `IMPL_PATH:`, `SPLIT:`, `TEST_PATH:`
# or `SUITE:` line; with none, the last result record. Input with no result record passes through unchanged.
#
# Usage:   extract-result.sh < leaf-stream.jsonl
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/extract_result.py" "$@"
