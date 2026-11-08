#!/bin/sh
# pin-reject-route.sh — route a verify-pin REJECT: a shim over veri/pin_reject_route.py.
#
# usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher>
# Exit:    0 the reason says the mutation stays green: the step retired, `retired` printed;
#          1 the reason does not say so; 2 a missing argument or no answer; 3 no unchecked step matched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_reject_route.py" "$@"
