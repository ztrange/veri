before 40
d660d33e605452c652f602287a1dd35143bf2528
keep 48
skills/tdd/scripts/tests/py/unit/test_pr_body.py
command 135
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_writes_a_run_part_holding_backslash_sequences_verbatim_3453

file 34
skills/tdd/scripts/veri/pr_body.py
old 14
lambda _: mine
new 4
mine
context 97
    body = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END), lambda _: mine, current, flags=re.S)
command 135
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_writes_a_run_part_holding_backslash_sequences_verbatim_3453

