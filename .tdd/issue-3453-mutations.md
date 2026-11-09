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

file 34
skills/tdd/scripts/veri/pr_body.py
old 19
        body = mine
new 29
        body = current + mine
context 19
        body = mine
command 153
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_on_a_legacy_body_with_no_run_markers_replaces_it_with_the_run_part_alone_3453

before 40
8817f984950f5c2b8cbba94646d48848fa0bc59f
keep 48
skills/tdd/scripts/tests/py/unit/test_pr_body.py
command 150
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_with_an_extra_argument_exits_2_with_the_usage_line_and_writes_nothing_3453

file 34
skills/tdd/scripts/veri/pr_body.py
old 14
len(argv) != 2
new 13
len(argv) < 2
context 22
    if len(argv) != 2:
command 150
make test TESTS=skills/tdd/scripts/tests/py/unit/test_pr_body.py::test_main_with_an_extra_argument_exits_2_with_the_usage_line_and_writes_nothing_3453

