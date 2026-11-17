#!/bin/sh
# lint-repair.sh — compose the repair step a red lint gets: a shim over veri/lint_repair.py.
#
# usage: lint-repair.sh step < <lint-output>
#
# stdout:  one line, `make `<command>` pass: <first finding> ⟦diff-checked⟧ ⟦lint-repair⟧`: the command the repo's
#          CLAUDE.md declares on `veri: lint:` (read here: a conductor Bash call shares no variable with an earlier
#          one), the output's first non-empty line capped at 200 characters, and every local path, the host and the
#          account name redacted, since the step is committed, pushed and mirrored to the issue.
# exit:    0 printed · 3 the repo declares no `veri: lint:` line · 2 bad arguments.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/lint_repair.py" "$@"
