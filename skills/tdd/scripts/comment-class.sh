#!/bin/sh
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`: a shim over veri/comment_class.py.
#
# usage: comment-class.sh [--sweepable] <file>…
#
# Class 1 is a comment in code, 2 a `#` line inside a heredoc redirected to a file or piped to tee, dd or sponge,
# 3 a `#` line inside any other heredoc, including one written to a `.md` file. --sweepable prints classes 1 and 2 only, less the comment block
# after a leading `#!` line, a `#!` line opening a heredoc's body and any comment starting `# hazard:` or `# pass-through:`.
#
# Exit: 0 printed, 2 bad arguments.
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/comment_class.py" "$@"
