#!/bin/sh
# pin-reject-route.sh — route a verify-pin REJECT: a shim over veri/pin_reject_route.py.
#
# usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher> <target-test>
# Exit:    0 the reason says the mutation stays green or has a before-state-green clause: the step retired, `retired` printed;
#          1 the reason does neither, or with --missing-reroute reports a surviving mutant of a
#          case red on the before-state (`revise` printed); 2 a missing argument (<target-test>
#          included: usage on stderr), no answer or a <target-test> that never ran (its file path does not
#          exist, or no tests ran: neither word printed), and with --missing-reroute a reason with
#          a before-state-green clause (a clause naming the before-state and green or pass, no fail/red/not/n't/after in it) (`unpinnable-missing` printed instead of `retired`/`revise`, the step left
#          unticked, an unpinnable-missing event appended);
#          3 no unchecked step matched
#
# Mode --recheck <reason-file> <ledger-file> <matcher> (routes a verify-refactor REJECT naming a pin): 0 `repin <file>` printed, a ⟦diff-checked⟧ re-pin step inserted
#          after the matched step; 1 `revise` (no "pin stayed green under its mutation/on the before-state: <file>" line) or
#          `repin-failed <file>` (a checked re-pin step for that file is already in the ledger), ledger untouched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_reject_route.py" "$@"
