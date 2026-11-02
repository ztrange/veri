file 46
skills/tdd/scripts/veri/build_verify_prompt.py
old 63
INTERFACE_PHASES + VERIFY_ONLY_PHASES, {"fast-cmd", "base-sha"}
new 42
INTERFACE_PHASES, {"fast-cmd", "base-sha"}
command 361
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpft7nxlj_/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py::test_main_refuses_a_beside_call_without_fast_cmd_or_without_a_base_sha_with_exit_2_as_the_other_interface_phases_do_2826

file 47
skills/tdd/scripts/prompts/develop-dual-stub.md
old 39
2. {{INCLUDE:_develop-run-affected.md}}
new 7
2. skip
command 346
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpft7nxlj_/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py::test_main_renders_a_dual_stub_prompt_that_runs_the_affected_suites_and_reports_transform_and_suite_2826

file 47
skills/tdd/scripts/prompts/develop-dual-stub.md
old 46
{{INCLUDE:_develop-transform-suite-report.md}}
new 0

command 346
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpft7nxlj_/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py::test_main_renders_a_dual_stub_prompt_that_runs_the_affected_suites_and_reports_transform_and_suite_2826

file 47
skills/tdd/scripts/veri/build_develop_prompt.py
old 40
ACCEPTED_WANT = {**WANT, "dual-stub": 4}
new 40
ACCEPTED_WANT = {**WANT, "dual-stub": 3}
command 343
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpft7nxlj_/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py::test_cli_dual_stub_with_too_few_arguments_exits_2_naming_the_four_it_needs_and_prints_no_prompt_2826

