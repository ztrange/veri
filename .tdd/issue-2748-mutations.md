file 59
skills/tdd/scripts/prompts/_affected-suites-working-tree.md
old 23
affected-suites.sh HEAD
new 14
FAST-TIER HEAD
command 295
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_develop_red_leaf_launched_alone_receives_the_affected_tier

file 43
skills/tdd/scripts/prompts/develop-green.md
old 14
`{{FAST_CMD}}`
new 6
`true`
command 306
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_develop_green_leaf_launched_alone_receives_the_fast_and_affected_tier

file 43
skills/tdd/scripts/prompts/develop-green.md
old 44
{{INCLUDE:_affected-suites-working-tree.md}}
new 1
x
command 306
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_develop_green_leaf_launched_alone_receives_the_fast_and_affected_tier

file 47
skills/tdd/scripts/veri/build_develop_prompt.py
old 24
"<fast-cmd>": "FAST_CMD"
new 25
"<fast-cmd>": "XFAST_CMD"
command 306
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_develop_green_leaf_launched_alone_receives_the_fast_and_affected_tier

file 46
skills/tdd/scripts/prompts/develop-refactor.md
old 42
Run the suites `affected-suites.sh` prints
new 41
Run the suites `all-the-suites.sh` prints
command 300
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_develop_refactor_leaf_launched_alone_receives_the_affected_tier

file 46
skills/tdd/scripts/veri/build_verify_prompt.py
old 31
if phase == "red" and fast_cmd:
new 9
if False:
command 318
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwzfvo3rc/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_run_conductor.py make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor.py::test_cli_2748_the_verify_red_leaf_given_fast_cmd_launched_alone_receives_the_fast_and_affected_tier

