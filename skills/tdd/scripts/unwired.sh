#!/bin/sh
# unwired.sh — the non-test files a range adds that no other non-test file names: a shim over veri/unwired.py.
#
# Prints, one per line, each path the range <branch-base>..HEAD adds that is not a test file and not under .tdd/,
# whose stem (basename without its last extension) no other non-test file git does not ignore holds as a whole
# word, `-` and `_` counted alike (PRD 031.4's walk); prose, config and data files and paths under .github/ are not
# checked, and a file the --accepted record lists (one path per line) is not printed. The Draft PR step's gate before
# the PR is readied (PRD 032.6).
#
# Usage:   unwired.sh [--accepted <record>] <branch-base>
# Exit:    1 one or more files printed; 0 every added file is named or accepted; 3 the range adds no such file;
#          2 bad arguments, the base does not resolve, or the directory is not a git work tree
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/unwired.py" "$@"
