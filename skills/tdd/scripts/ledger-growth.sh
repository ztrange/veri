#!/bin/sh
# ledger-growth.sh — check a ledger's growth against the plan commit's: a shim over veri/ledger_growth.py.
#
# usage: ledger-growth.sh <plan-ledger-file> <ledger-file>
#        ledger-growth.sh plan-sha    (stdin: the git log, one "<sha> <subject>" line per commit)
#
# plan-sha prints the newest `plan: scope` or `plan: rewrite` commit, the baseline whose ledger is
# <plan-ledger-file>, so a rewrite after a verify-plan REJECT replaces the first plan commit.
# Records: every step line the plan did not hold must equal a line add-ledger-step.sh wrote to the
# tracked issue-<n>-added.md beside the ledger, or one of its step-added events in events.jsonl.
# Exit:    0 every new line is recorded and carries ⟦added⟧ (a recorded repair or --planned line
#          need not), and the ⟦added⟧ lines are within VERI_STEP_GROWTH;
#          1 a new line lacks its record or ⟦added⟧, or the cap is passed, named on stderr;
#          2 a missing argument, an unreadable ledger or plan file, a bad VERI_STEP_GROWTH, or
#          (plan-sha) no plan commit in the log
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/ledger_growth.py" "$@"
