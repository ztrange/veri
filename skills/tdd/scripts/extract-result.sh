#!/bin/sh
# extract-result.sh — pull the final assistant text out of a claude stream-json stream: a shim over veri/extract_result.py.
#
# Writes the newest result record whose text carries a `VERDICT:`, `IMPL_PATH:`, `SPLIT:`, `TEST_PATH:`
# or `SUITE:` line; with none, the last result record. Input with no result record passes through unchanged.
#
# Usage:   extract-result.sh < leaf-stream.jsonl
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/extract_result.py" "$@"
