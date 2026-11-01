file 35
skills/tdd/scripts/veri/tunables.py
old 34
Tunable(rebased_tip_suite, "local"
new 31
Tunable(rebased_tip_suite, "ci"
command 284
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp1vidpx7p/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_tunables.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_tunables.py::test_2841_rebased_tip_suite_unset_resolves_to_local_with_no_error

file 35
skills/tdd/scripts/veri/tunables.py
old 26
raw not in ("local", "ci")
new 21
raw not in ("local",)
command 285
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp1vidpx7p/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_tunables.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_tunables.py::test_2841_rebased_tip_suite_set_to_ci_resolves_to_ci_with_no_error

file 19
skills/tdd/SKILL.md
old 54
under `ci` run no full test command on the rebased tip
new 48
in the other mode run nothing on the rebased tip
command 247
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdteuonur/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py

file 19
skills/tdd/SKILL.md
old 34
under `ci`, that push with no full
new 33
otherwise, that push with no full
command 247
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdteuonur/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py

file 19
skills/tdd/SKILL.md
old 51
on the rebased tip (under `ci`, none), and the push
new 32
on the rebased tip, and the push
command 247
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdteuonur/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_skill_rebased_tip_suite.py

