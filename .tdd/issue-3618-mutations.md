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

before 40
85e5f2a9f1ed9c52291524810ca97b5de58a12c7
keep 56
skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py
command 164
make test TESTS=skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py::test_main_3618_stderr_states_the_uncommitted_step_is_not_durable_when_no_conductor_is_live

