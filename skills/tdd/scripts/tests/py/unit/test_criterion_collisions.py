"""Cases for veri/criterion_collisions.py."""
import importlib

SPEC = """## Acceptance criteria
- [x] src/auth.tsx no longer asserts non-null
- [ ] src/auth.test.tsx fails when the guard is reverted

## Blocked by
- [ ] src/never.py is not a criterion
"""


def test_2506_a_changed_file_a_criterion_names_is_reported_with_the_criterion_and_others_are_not():
    collisions = importlib.import_module("veri.criterion_collisions").collisions

    assert collisions(SPEC, ["src/auth.tsx", "src/never.py", "lib/other.py"]) == ["src/auth.tsx: criterion 1"]


def test_2506_bad_arguments_exit_2_with_the_usage(run_cli):
    module = importlib.import_module("veri.criterion_collisions")

    code, out, err = run_cli(module, [])

    assert (code, out, err.startswith("usage: criterion-collisions.sh")) == (2, "", True)
