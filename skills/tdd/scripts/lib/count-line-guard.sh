#!/usr/bin/env bash
# lib/count-line-guard.sh — sourced, not run: defines the count-line guard every suite is held to.
#
# COUNT_LINE — the ERE a suite's last line must match.
# COUNTLESS  — a printf format taking the suite's name, printed for a suite whose last line does not.
COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'
COUNTLESS='%s: never reached its count line\n'
