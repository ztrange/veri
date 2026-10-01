#!/usr/bin/env bash
# extract-result.sh — pull the final assistant text out of a claude stream-json stream.
#
# `claude -p --output-format stream-json --verbose` emits one JSON object per line; the
# terminal `{"type":"result", ..., "result":"<text>"}` event carries the clean final
# answer (the same text plain mode would print). This reads that stream on stdin and
# writes the result text on stdout, so parse-verdict.sh can read a clean VERDICT block.
#
# If the input contains no stream-json result event (e.g. a plain-text leaf, or a test
# stub), the input is passed through unchanged — extraction is a no-op on non-stream data.
#
# A leaf re-invoked after it answered (a background task completing) writes a
# later result record with no verdict in it, so the newest record whose text carries a
# `VERDICT:` line wins over a merely newer one; with none, the last record wins.
#
# Usage:   extract-result.sh < leaf-stream.jsonl
#
# Passed via `python3 -c` (not a heredoc) so the leaf stream stays on stdin.
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"

exec python3 -c '
import sys, json, re
data = sys.stdin.read()
result = None
verdict = None
verdict_re = re.compile(r"^[ \t]*verdict:", re.I | re.M)
for line in data.splitlines():
    s = line.strip()
    if not s.startswith("{"):
        continue
    try:
        obj = json.loads(s)
    except ValueError:
        continue
    if isinstance(obj, dict) and obj.get("type") == "result" and "result" in obj:
        result = obj["result"]          # last result event wins
        if isinstance(result, str) and verdict_re.search(result):
            verdict = result            # ...unless a later one carries no verdict
if verdict is not None:
    result = verdict
if result is None:
    sys.stdout.write(data)              # not a stream-json result -> passthrough
else:
    sys.stdout.write(result if result.endswith("\n") else result + "\n")
'
