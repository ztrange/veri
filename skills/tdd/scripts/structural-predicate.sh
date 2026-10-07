#!/bin/sh
# structural-predicate.sh <record> — read a predicate leaf's report on stdin and write its
# `PREDICATE:` command to <record>: a shim over veri/structural_predicate.py.
#
# usage: structural-predicate.sh <record>
#        structural-predicate.sh .tdd/issue-<n>-predicate < <leaf-report>
#
# exit:  0 the command was written; 1 the command already succeeds on the current tree,
#        nothing written; 2 bad arguments, or no `PREDICATE:` line; 3 `PREDICATE: NONE [— <why>]`,
#        `NONE—<why>` or `NONE: <why>`, nothing written.
exec python3 "$(dirname "$0")/veri/structural_predicate.py" "$@"
