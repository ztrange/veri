# Mutation-parity pairs for #1375

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| `a script requiring a positional argument exits 2 with a usage line when called with none` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none` | `1a-no-argument-exits-1.patch` | proven |
| `a script requiring a positional argument exits 2 with a usage line when called with none` | `tests/py/unit/test_missing_argument_cli.py::test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none` | `1b-usage-on-stdout.patch` | proven |
