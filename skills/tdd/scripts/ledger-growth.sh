#!/bin/sh
# ledger-growth.sh — check a ledger's growth against the plan commit's: a shim over veri/ledger_growth.py.
#
# usage: ledger-growth.sh <plan-ledger-file> <ledger-file> | plan-sha | record-existing <ledger-file>
#        | record-rewrite <pre-rewrite-ledger-file> <ledger-file> | reopen <ledger-file> <needle> <change>
#        | split <ledger-file>
#        plan-sha reads the git log on stdin, one "<sha> <subject>" line per commit.
#
# diff-leaf-deviation.sh is the sibling check on a diff-checked leaf's commits.
# plan-sha prints the newest `plan: scope` or `plan: rewrite` commit, the baseline whose ledger is
# <plan-ledger-file>, so a rewrite after a verify-plan REJECT replaces the first plan commit.
# Records: every step line the plan did not hold must equal a line add-ledger-step.sh wrote to the
# tracked issue-<n>-added.md beside the ledger, or one of its step-added events in events.jsonl.
# Exit:    0 every new line is recorded and carries ⟦added⟧ (a recorded repair or --planned line
#          need not), and the ⟦added⟧ lines are within ⌈VERI_STEP_GROWTH_PERCENT × P ÷ 100⌉,
#          P the steps in <plan-ledger-file>;
#          1 a new line lacks its record or ⟦added⟧, or the cap is passed, named on stderr;
#          2 a missing argument, an unreadable ledger or plan file, a bad VERI_STEP_GROWTH_PERCENT,
#          the retired absolute-count knob set, or
#          (plan-sha) no plan commit in the log
# split:   0 the ledger's steps N exceed P, those of the ledger at the oldest `plan: scope` commit of its
#          history, by more than ⌈VERI_STEP_GROWTH_PERCENT × P ÷ 100⌉ (⟦suite-repair⟧ and ⟦ci-repair⟧ lines
#          uncounted): prints the growth line and the criterion boundary to split at; 3 within it, printing nothing;
#          2 a missing or extra argument, an unreadable ledger or history, no `plan: scope` commit, a bad
#          VERI_STEP_GROWTH_PERCENT or the retired knob set. It refuses nothing and writes nothing.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ledger_growth.py" "$@"
