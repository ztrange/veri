#!/bin/sh
# parse-verdict.sh — extract a blind verifier leaf's structured verdict from its output: a shim over veri/parse_verdict.py.
#
# A verifier leaf ends its output with a verdict block:
#
#     VERDICT: PASS | REJECT
#     REASON: <one or more lines of justification>
#
# The LAST `VERDICT:` line is the authoritative one. The reason may be given on a following
# `REASON:` line (possibly multi-line) or inline after the verdict word (`VERDICT: REJECT — <reason>`).
#
# usage:   parse-verdict.sh < leaf-output.txt
#
# stdout:  the reason text (the human-facing justification), trimmed.
# exit:    0 PASS · 1 REJECT · 2 malformed/no recognisable verdict (stdout empty,
#          a diagnostic on stderr).
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/parse_verdict.py" "$@"
