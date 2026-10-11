#!/usr/bin/env bash
# Unit tests for scripts/leaf-launchable.sh — the preflight check that a leaf can actually
# be LAUNCHED.
#
# Contract under test:
#   Every case moved to tests/py/test_leaf_launchable.py; this suite holds none.
#     refuses when the leaf binary cannot launch
#       → test_main_prints_the_failed_probe_diagnostic_byte_identical_to_the_bash_script_indenting_its_stderr_as_bytes_split_on_newline_only
#     refuses without a side effect
#       → test_run_cli_refusing_a_binary_that_cannot_launch_starts_nothing_but_the_probe_and_leaves_no_file
#     passes when the leaf binary launches
#       → test_main_returns_0_silently_for_a_launching_probe_with_or_without_an_argument_and_2_with_no_stdout_for_a_failing_one
#     run through a symlink to the skill directory answers as in place
#       → test_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_answers_as_run_in_place_for_a_launching_and_a_failing_binary
#
# Run: scripts/tests/leaf-launchable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

finish
