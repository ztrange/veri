file 56
skills/tdd/scripts/tests/py/unit/test_scripts_md_rows.py
old 46
    return sorted(listed - bullets - excluded)
new 83
    return sorted(n for n in listed - excluded if not any(n in b for b in bullets))
context 46
    return sorted(listed - bullets - excluded)
command 134
make test TESTS=skills/tdd/scripts/tests/py/unit/test_scripts_md_rows.py::test_bullet_names_are_compared_whole_not_by_containment_3565

file 56
skills/tdd/scripts/tests/py/unit/test_scripts_md_rows.py
old 46
    return sorted(listed - bullets - excluded)
new 83
    return sorted(n for n in listed - excluded if not any(b in n for b in bullets))
context 46
    return sorted(listed - bullets - excluded)
command 134
make test TESTS=skills/tdd/scripts/tests/py/unit/test_scripts_md_rows.py::test_bullet_names_are_compared_whole_not_by_containment_3565

