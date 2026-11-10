file 39
skills/tdd/scripts/veri/tests_frozen.py
old 78
repaired = any(l.startswith("- [x]") and "⟦suite-repair⟧" in l for l in lines)
new 15
repaired = True
context 82
    repaired = any(l.startswith("- [x]") and "⟦suite-repair⟧" in l for l in lines)
command 150
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_still_refuses_a_case_an_ordinary_green_rewrote_3541

