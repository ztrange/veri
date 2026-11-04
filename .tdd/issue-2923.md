# Plan for #2923 — build-develop-prompt.sh usage, SCRIPTS.md and REVISE.md omit the beside and dual-stub phases

- [x] The older cases in skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py that compare build-develop-prompt.sh's usage line verbatim take that line from the module's own USAGE rather than from a literal phase list, so the usage line may gain a phase without turning them red; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] build-develop-prompt.sh called with no arguments exits 2 and prints a usage line on stderr whose phase list names dual-stub and still names beside ⟦criterion 1⟧
- [x] skills/tdd/SCRIPTS.md: its build-develop-prompt.sh phase list names beside, cover-new and dual-stub, as requirement SC7 states ⟦skill-edit⟧ ⟦criterion 2⟧
- [x] skills/tdd/REVISE.md: its list of the phases sent to build-develop-prompt.sh revise <phase> names beside, cover-new and dual-stub, as requirement RV4 states ⟦skill-edit⟧ ⟦criterion 3⟧
- [x] fix the full-suite failure: skills/tdd/scripts/tests/py/test_shims.py — FAILED skills/tdd/scripts/tests/py/test_shims.py::test_every_real_shim_is_executable_so_running_it_does_not_exit_126 - AssertionError: assert ['suite-flakes.sh'] == [] ⟦suite-repair⟧ ⟦criterion 3⟧
