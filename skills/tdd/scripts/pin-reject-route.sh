#!/bin/sh
# pin-reject-route.sh — route a verify-pin REJECT: a shim over veri/pin_reject_route.py.
#
# usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher> <target-test>
# Exit:    0 the reason says the mutation stays green: the step retired, `retired` printed;
#          1 the reason does not say so (`revise` printed); 2 a missing argument (<target-test>
#          included: usage on stderr), no answer or a <target-test> that never ran (its file path does not
#          exist, or no tests ran: neither word printed), and with --missing-reroute a reason that says
#          "stays green" (the step is left unticked, an unpinnable-missing event appended);
#          3 no unchecked step matched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_reject_route.py" "$@"
