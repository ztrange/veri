# Mutation-parity pairs for #1375

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| `a script requiring a positional argument exits 2 with a usage line when called with none` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none` | `1a-no-argument-exits-1.patch` | proven |
| `a script requiring a positional argument exits 2 with a usage line when called with none` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none` | `1b-usage-on-stdout.patch` | proven |
| `a script exits 2 with a usage line when a later required argument is missing` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_exits_2_with_a_usage_line_when_a_later_required_argument_is_missing` | `2a-missing-cmd-exits-1.patch` | proven |
| `a script given a bad argument value exits 2 with its own usage text on stderr` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_given_a_bad_argument_value_exits_2_with_its_own_usage_text_on_stderr` | `2b-unknown-cause-exits-1.patch` | proven |
| `migration slice 6 refuses an unresolvable commit or a missing file with the script's own usage text` | `tests/py/unit/test_missing_argument_cli.py::test_migration_slice_6_refuses_an_unresolvable_commit_or_a_missing_file_with_the_scripts_own_usage_text` | `2c-missing-file-exits-1.patch` | proven |
