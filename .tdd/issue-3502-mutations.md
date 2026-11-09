file 34
skills/tdd/scripts/veri/pr_body.py
old 5
".*?"
new 4
".*"
context 73
    pattern = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.S)
command 136
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_keeps_foreign_text_between_two_run_parts_byte_identical_3502

