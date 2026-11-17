#!/bin/sh
# tidy-first.sh — read a green leaf's `TIDY_FIRST:` answer: a shim over veri/tidy_first.py.
#
# A green leaf that sees the step would be one small change after a behaviour-preserving
# restructuring of code already committed answers one line,
# `TIDY_FIRST: <refactoring> | <file>::<symbol> | <why>`, the refactoring a name skills/tdd/SMELLS.md lists.
#
# usage: tidy-first.sh < <green-report>
#
# stdout:  the `⟦diff-checked⟧` step the line asks for: the refactoring, the file and symbol, and that
#          the step changes no behaviour and no test file. Never the <why>: the text reaches the blind
#          diff verifier, and the why is the developer's rationale.
# exit:    0 printed · 3 the report has no `TIDY_FIRST:` line · 1 the leaf answered wrongly (stdout empty,
#          one stderr line naming the offending line): two or more such lines, a line not of that form, a
#          refactoring SMELLS.md does not list, an absolute path, or a file absent from the working tree ·
#          2 no answer could be read: an argument, or SMELLS.md unreadable.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tidy_first.py" "$@"
