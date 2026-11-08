before 40
eca23e109ec95c824fa3b9f7120b7ef687d45092
keep 57
skills/tdd/scripts/tests/py/unit/test_pin_reject_route.py
command 437
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpwn8uyvz0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_pin_reject_route.py::test_main_usage_on_too_few_arguments_and_nonzero_unpinnable_exit_passes_through_without_retired_3300 make test TESTS=skills/tdd/scripts/tests/py/unit/test_pin_reject_route.py::test_main_usage_on_too_few_arguments_and_nonzero_unpinnable_exit_passes_through_without_retired_3300

file 43
skills/tdd/scripts/veri/pin_reject_route.py
old 17
    if code == 0:
new 12
    if True:
command 175
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pin_reject_route.py::test_main_usage_on_too_few_arguments_and_nonzero_unpinnable_exit_passes_through_without_retired_3300

file 47
skills/tdd/scripts/veri/build_develop_prompt.py
old 25
rb"^REASON:.*stays green"
new 12
rb"^REASON:"
command 181
make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt_pin_reject.py::test_revise_red_for_a_verify_pin_reason_not_saying_stays_green_still_builds_the_prompt_3300

file 47
skills/tdd/scripts/veri/build_develop_prompt.py
old 51
phase == "revise" and revised_phase == "red" and os
new 24
phase == "revise" and os
command 179
make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt_pin_reject.py::test_revise_green_for_a_verify_pin_reason_saying_stays_green_still_builds_the_prompt_3300

