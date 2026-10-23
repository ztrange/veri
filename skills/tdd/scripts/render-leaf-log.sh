#!/bin/sh
# render-leaf-log.sh — turn a leaf's stream-json log into the readable lines the
# dashboard's Chatter pane shows: a shim over veri/render_leaf_log.py. One line per thing said or done:
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
# usage:   render-leaf-log.sh < .tdd/LEAF.out   (takes no argument)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/render_leaf_log.py"
