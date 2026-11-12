file 42
skills/tdd/scripts/veri/add_ledger_step.py
old-b64 32
aWYgZG9uZS5yZXR1cm5jb2RlID09IDA6
new-b64 12
aWYgVHJ1ZTo=
context-b64 40
ICAgIGlmIGRvbmUucmV0dXJuY29kZSA9PSAwOg==
command 142
make test TESTS=skills/tdd/scripts/tests/py/test_add_ledger_step_process.py::test_cli_3618_stdout_makes_no_durable_claim_when_the_commit_fails

before 40
d3bf1e722b554059a6af343615557d62d6367056
keep 59
skills/tdd/scripts/tests/py/test_add_ledger_step_process.py
command 173
make test TESTS=skills/tdd/scripts/tests/py/test_add_ledger_step_process.py::test_cli_3618_stderr_states_the_committed_step_is_durable_naming_the_commit_leaving_stdout_empty

