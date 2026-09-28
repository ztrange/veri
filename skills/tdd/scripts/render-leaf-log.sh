#!/usr/bin/env bash
# render-leaf-log.sh — turn a leaf's stream-json log into the readable lines the
# dashboard's Chatter pane shows. One line per thing said or done:
#
#   <assistant text>                  what the leaf said
#   > <tool>: <first input line>      a tool call, with the first line of its input
#   < <tool result>                   the result's first line, cut to 80 characters,
#                                     with `…` marking that something was cut
#
# Everything else — the system init, thinking blocks, the terminal result record —
# prints nothing. A line that is not JSON exits 2 and prints nothing at all: the
# rendering is written only after the loop, so the records already rendered are
# discarded along with the line that stopped it.
#
# Usage:   render-leaf-log.sh < .tdd/<leaf>.out
#
# Passed via `python3 -c` (not a heredoc) so the leaf log stays on stdin.
set -euo pipefail

exec python3 -c '
import sys, json

def first_line(text):
    return (text.splitlines() or [""])[0]

def truncated(text, limit):
    head = first_line(text)
    cut = len(text.splitlines()) > 1 or len(head) > limit
    return head[:limit] + ("…" if cut else "")

out = []
for line in sys.stdin:
    try:
        obj = json.loads(line)
    except ValueError:
        sys.stderr.write("render-leaf-log.sh: not JSON: %s" % line)
        sys.exit(2)
    content = (obj.get("message") or {}).get("content") or []
    for block in content:
        kind = block.get("type")
        if kind == "text":
            out.append(block["text"])
        elif kind == "tool_use":
            values = list(block.get("input", {}).values())
            arg = first_line(str(values[0])) if values else ""
            out.append("> %s: %s" % (block["name"], arg))
        elif kind == "tool_result":
            out.append("< " + truncated(str(block.get("content", "")), 80))
sys.stdout.write("".join(l + "\n" for l in out))
'
