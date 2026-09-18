#!/usr/bin/env bash
# render-leaf-log.sh — turn a leaf's stream-json log into the readable lines the
# dashboard's Chatter pane shows (issue #255). One line per thing said or done:
#
#   <assistant text>                  what the leaf said
#   > <tool>: <first input line>      a tool call, with the first line of its input
#   < <tool result>                   the result's first line, cut to 80 characters,
#                                     with `…` marking that something was cut
#
# Everything else — the system init, thinking blocks, the terminal result record —
# prints nothing.
#
# Usage:   render-leaf-log.sh < .tdd/<leaf>.out
#
# Passed via `python3 -c` (not a heredoc) so the leaf log stays on stdin.
set -euo pipefail

exec python3 -c '
import sys, json

def first_line(text, limit=None):
    lines = text.splitlines() or [""]
    head = lines[0]
    cut = len(lines) > 1
    if limit is not None and len(head) > limit:
        head, cut = head[:limit], True
    return head + ("…" if cut else "")

out = []
for line in sys.stdin:
    obj = json.loads(line)
    content = (obj.get("message") or {}).get("content") or []
    for block in content:
        kind = block.get("type")
        if kind == "text":
            out.append(block["text"])
        elif kind == "tool_use":
            values = list(block.get("input", {}).values())
            arg = (str(values[0]).splitlines() or [""])[0] if values else ""
            out.append("> %s: %s" % (block["name"], arg))
        elif kind == "tool_result":
            out.append("< " + first_line(str(block.get("content", "")), 80))
sys.stdout.write("".join(l + "\n" for l in out))
'
